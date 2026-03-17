"""
bot.py — Core selfbot logic.

- Reads Discord embeds for queue detection
- Stray mode: notify user when a game is posted (no clicking)
- Windows notification + sound on queue join and stray game
- Pings user in Discord when queue is joined
"""

import discord
import asyncio
import re
import os
import sys
import threading
from logger import setup_logger, log_queue_event

logger = setup_logger()
warn_callback     = None
gui_log_callback  = None
notify_callback   = None
last_seen_callback   = None  # called when a queue opens: (server_name, time_str)
status_dot_callback  = None  # called to update queue status dot: (server_name, is_open)
joined_callback      = None  # called when bot joins a queue: (server_name) — uncheck others


def _gui_log(msg: str):
    if gui_log_callback:
        try: gui_log_callback(msg)
        except: pass

def _notify(title: str, message: str):
    if notify_callback:
        try: notify_callback(title, message)
        except: pass


# Volume level 0.0 - 1.0 (set by GUI)
sound_volume = 1.0

def _get_sound_path():
    """Always return notification.wav next to the executable."""
    import pathlib as _pl, sys as _sys
    base = _pl.Path(_sys.executable).parent if getattr(_sys, "frozen", False) else _pl.Path(__file__).parent
    return str(base / "notification.wav")

def play_sound():
    """Play notification.wav at the configured volume."""
    def _play():
        try:
            import winsound, wave, struct, tempfile, shutil
            sound_path = _get_sound_path()
            if not os.path.exists(sound_path):
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                return

            vol = max(0.0, min(1.0, sound_volume))

            if vol >= 0.99:
                # Full volume — play directly
                winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                return

            # Scale volume by adjusting PCM samples
            with wave.open(sound_path, "rb") as w:
                params = w.getparams()
                frames = w.readframes(params.nframes)

            # Scale 16-bit samples
            samples = struct.unpack(f"<{len(frames)//2}h", frames)
            scaled = struct.pack(f"<{len(samples)}h",
                                 *[max(-32768, min(32767, int(s * vol))) for s in samples])

            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            with wave.open(tmp.name, "wb") as w:
                w.setparams(params)
                w.writeframes(scaled)

            winsound.PlaySound(tmp.name, winsound.SND_FILENAME)
            os.unlink(tmp.name)

        except Exception as e:
            try:
                import winsound
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except Exception:
                pass
    threading.Thread(target=_play, daemon=True).start()


def windows_toast(title: str, body: str):
    """Show a Windows 10/11 toast notification."""
    try:
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast(title, body, duration=6, threaded=True)
    except Exception:
        # Fallback: try winotify
        try:
            from winotify import Notification
            toast = Notification(app_id="QUEUE BOT", title=title, msg=body)
            toast.show()
        except Exception:
            pass  # Notifications not available — silent fail


class QueueBot(discord.Client):

    def __init__(self, config: dict, enabled_server_ids: set):
        super().__init__()
        self.config = config
        self.enabled_server_ids = enabled_server_ids
        self.leave_threshold = config.get("leave_threshold", 10)
        self.click_delay     = config.get("click_delay", 0.5)

        self.joined:  dict[int, bool] = {}
        self.warned:  dict[int, bool] = {}
        self.last_seen: dict[int, str] = {}
        self.watched_channels: dict[int, dict] = {}

        for server in config["servers"]:
            self.watched_channels[server["queue_channel_id"]] = server
            self.joined[server["guild_id"]] = False
            self.warned[server["guild_id"]] = False
            self.last_seen[server["guild_id"]] = "Never"

    def _bot_id(self, server_cfg: dict) -> int:
        return int(server_cfg.get("queue_bot_id",
               self.config.get("default_queue_bot_id", 1308417680361000970)))

    def _is_stray(self, server_cfg: dict) -> bool:
        return server_cfg.get("stray_mode", False) or server_cfg.get("group") == "hungergames"

    def _extract_queue_size(self, full_text: str):
        """Extract current queue size from text like 'Queue (13/20)' or '13/20'."""
        patterns = [
            r'queue\s*\((\d+)/\d+\)',
            r'\((\d+)/\d+\)',
            r'(\d+)\s*/\s*\d+\s*(?:players|in queue)',
        ]
        for pattern in patterns:
            m = re.search(pattern, full_text.lower())
            if m:
                return int(m.group(1))
        return None

    # ------------------------------------------------------------------
    # Extract full text from message + embeds
    # ------------------------------------------------------------------

    def _full_text(self, message: discord.Message) -> str:
        parts = [message.content or ""]
        for embed in message.embeds:
            if embed.title:       parts.append(embed.title)
            if embed.description: parts.append(embed.description)
            for field in embed.fields:
                if field.name:  parts.append(field.name)
                if field.value: parts.append(field.value)
            if embed.footer and embed.footer.text:
                parts.append(embed.footer.text)
        return "\n".join(parts)

    def _extract_time(self, full_text: str) -> str:
        """Try to extract a time string from the message (e.g. '8:00 PM', '20:00')."""
        patterns = [
            r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)\b',
            r'\b\d{1,2}:\d{2}\b',
            r'\b\d{1,2}\s*(?:AM|PM|am|pm)\b',
            r'<t:\d+(?::[tTdDfFR])?>'   # Discord timestamp
        ]
        for pattern in patterns:
            match = re.search(pattern, full_text)
            if match:
                return match.group(0)
        return ""

    def _is_queue_open(self, full_text: str, server_cfg: dict) -> bool:
        t = full_text.lower()
        closed_kws = server_cfg.get("queue_closed_keywords", [])
        if any(kw.lower() in t for kw in closed_kws):
            return False
        open_kws = server_cfg.get("queue_open_keywords", [])
        if open_kws and any(kw.lower() in t for kw in open_kws):
            return True
        closed_phrases = ["not available", "unavailable", "closed",
                          "no testers", "queue is closed", "queue is full"]
        open_phrases   = ["tester(s) available", "testers available",
                          "available!", "queue is open", "join queue",
                          "now open", "queue ("]
        if any(p in t for p in closed_phrases):
            return False
        return any(p in t for p in open_phrases)

    def _is_real_queue_message(self, message: discord.Message) -> bool:
        full = self._full_text(message)
        stripped = full.strip().lower()
        if stripped in ("@here", "@everyone", ""):
            return False
        queue_words = ["available", "tester", "queue", "waitlist",
                       "waiting list", "join", "open", "closed", "game", "stray"]
        return any(w in stripped for w in queue_words)

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    async def on_ready(self):
        m = f"Logged in as {self.user} ({self.user.id})"
        logger.info(m); _gui_log(m)
        m = f"Watching {len(self.watched_channels)} queue channel(s)"
        logger.info(m); _gui_log(m)
        for server in self.config["servers"]:
            status = "AUTO-JOIN ON" if server["guild_id"] in self.enabled_server_ids else "LOG ONLY"
            tag    = f"[{server.get('group','?').upper()}]"
            m = f"  [{status}] {tag} {server['name']}"
            logger.info(m); _gui_log(m)
        m = "Scanning channels for active queues on startup..."
        logger.info(m); _gui_log(m)
        await self.check_all_queues_on_startup()

    async def check_all_queues_on_startup(self):
        for server in self.config["servers"]:
            try:
                channel = self.get_channel(server["queue_channel_id"])
                if channel is None:
                    m = f"[{server['name']}] Queue channel not found"
                    logger.warning(m); _gui_log("⚠ " + m)
                    continue

                bot_id = self._bot_id(server)
                found  = False
                any_bot = server.get("any_bot", False)
                import datetime as _dt
                now_utc = _dt.datetime.now(_dt.timezone.utc)
                async for msg in channel.history(limit=50):
                    if not any_bot and msg.author.id != bot_id:
                        continue
                    if any_bot and not msg.author.bot:
                        continue
                    # Skip messages older than 5 minutes on startup
                    age = (now_utc - msg.created_at).total_seconds()
                    if age > 300:
                        log_queue_event(logger, server["name"], "STARTUP SKIP — message too old",
                                        f"{int(age)}s old")
                        continue
                    if not self._is_real_queue_message(msg):
                        continue
                    full = self._full_text(msg)
                    m = f"[{server['name']}] FOUND MESSAGE ON STARTUP | \"{full[:80]}\""
                    logger.info(m); _gui_log(m)
                    await self.evaluate_queue_state(msg, server, source="STARTUP")
                    found = True
                    break

                if not found:
                    m = f"[{server['name']}] No queue message found (likely closed)"
                    logger.info(m); _gui_log(m)

            except discord.Forbidden:
                m = f"[{server['name']}] No permission to read queue channel"
                logger.warning(m); _gui_log("⚠ " + m)
            except Exception as e:
                m = f"[{server['name']}] Startup check error: {e}"
                logger.warning(m); _gui_log("⚠ " + m)

    async def on_message(self, message: discord.Message):
        if message.channel.id not in self.watched_channels:
            return
        server_cfg = self.watched_channels[message.channel.id]
        # any_bot mode: accept messages from any bot in the channel
        if not server_cfg.get("any_bot", False):
            if message.author.id != self._bot_id(server_cfg):
                return
        elif not message.author.bot:
            return  # still only accept bots, just any bot

        full = self._full_text(message)
        m = f"[{server_cfg['name']}] NEW MESSAGE | \"{full[:80]}\""
        logger.info(m); _gui_log(m)
        await self.evaluate_queue_state(message, server_cfg, source="NEW MESSAGE")

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if after.channel.id not in self.watched_channels:
            return
        server_cfg = self.watched_channels[after.channel.id]
        if not server_cfg.get("any_bot", False):
            if after.author.id != self._bot_id(server_cfg):
                return
        elif not after.author.bot:
            return

        full_before = self._full_text(before)
        full_after  = self._full_text(after)
        if full_before.strip() == full_after.strip():
            return

        m = f"[{server_cfg['name']}] MESSAGE EDITED | \"{full_before[:40]}\" -> \"{full_after[:40]}\""
        logger.info(m); _gui_log(m)
        await self.evaluate_queue_state(after, server_cfg, source="EDIT")

    async def on_message_delete(self, message: discord.Message):
        if message.channel.id not in self.watched_channels:
            return
        server_cfg = self.watched_channels[message.channel.id]
        if not server_cfg.get("any_bot", False):
            if message.author.id != self._bot_id(server_cfg):
                return
        elif not message.author.bot:
            return

        guild_id = server_cfg["guild_id"]
        m = f"[{server_cfg['name']}] MESSAGE DELETED — Queue closed"
        logger.info(m); _gui_log(m)
        self.joined[guild_id] = False
        self.warned[guild_id] = False

    # ------------------------------------------------------------------
    # Core logic
    # ------------------------------------------------------------------

    async def evaluate_queue_state(self, message: discord.Message,
                                    server_cfg: dict, source: str = ""):
        server_name = server_cfg["name"]
        guild_id    = server_cfg["guild_id"]
        full_text   = self._full_text(message)

        # ── STRAY MODE ─────────────────────────────────────────────────
        if self._is_stray(server_cfg):
            if int(guild_id) not in {int(x) for x in self.enabled_server_ids}:
                m = f"[{server_name}] HUNGER GAMES LOG ONLY — notifications off"
                logger.info(m); _gui_log(m)
                return

            game_time = self._extract_time(full_text)
            if game_time:
                m = f"[{server_name}] 🎮 GAME DETECTED at {game_time}!"
                toast_msg = f"A game is happening at {game_time}"
            else:
                m = f"[{server_name}] 🎮 GAME DETECTED!"
                toast_msg = "A game is happening!"
            logger.info(m); _gui_log("🎮 " + m)

            play_sound()
            windows_toast("🎮 Game Alert!", toast_msg)
            _notify("🎮 Game Alert!", toast_msg)
            return

        # ── NORMAL QUEUE MODE ──────────────────────────────────────────
        is_open = self._is_queue_open(full_text, server_cfg)

        # Always update last seen when we get any message from this server's bot
        import datetime
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.last_seen[guild_id] = now
        if last_seen_callback:
            last_seen_callback(server_name, now)

        if is_open:
            if status_dot_callback:
                status_dot_callback(server_name, True)
            m = f"[{server_name}] QUEUE OPEN [{source}]"
            logger.info(m); _gui_log("🟢 " + m)

            # Log the full queue message so user can see the player list
            separator = "─" * 40
            for line in full_text.strip().split("\n"):
                line = line.strip()
                if line:
                    logger.info(f"  {line}")
                    _gui_log(f"  {line}")
            _gui_log(f"  {separator}")

            if int(guild_id) not in {int(x) for x in self.enabled_server_ids}:
                m = f"[{server_name}] LOG ONLY — skipping auto-join"
                logger.info(m); _gui_log(m)
                return

            # Check queue size — don't join if 11+ players already in queue
            queue_size = self._extract_queue_size(full_text)
            if queue_size is not None and queue_size >= 11:
                m = f"[{server_name}] QUEUE TOO FULL ({queue_size} players) — skipping"
                logger.info(m); _gui_log("🚫 " + m)
                return

            if self.joined.get(guild_id):
                m = f"[{server_name}] Already in queue — checking position"
                logger.info(m); _gui_log(m)
                await self.check_position(message, server_cfg)
                return

            m = f"[{server_name}] Joining in {self.click_delay}s..."
            logger.info(m); _gui_log(m)
            await asyncio.sleep(self.click_delay)
            await self.click_join_button(message, server_cfg)
        else:
            if self.joined.get(guild_id):
                m = f"[{server_name}] Queue closed — resetting state"
                logger.info(m); _gui_log(m)
            if status_dot_callback:
                status_dot_callback(server_name, False)
            self.joined[guild_id] = False
            self.warned[guild_id] = False

    async def click_join_button(self, message: discord.Message, server_cfg: dict):
        server_name = server_cfg["name"]

        if not message.components:
            m = f"[{server_name}] ERROR — No buttons found on message"
            logger.error(m); _gui_log("❌ " + m)
            return

        for action_row in message.components:
            for component in action_row.children:
                if isinstance(component, discord.Button):
                    try:
                        await component.click()
                        self.joined[server_cfg["guild_id"]] = True
                        self.warned[server_cfg["guild_id"]] = False

                        m = f"[{server_name}] ✅ JOINED QUEUE — Clicked: '{component.label}'"
                        logger.info(m); _gui_log("✅ " + m)

                        # 🔔 Notify user they joined
                        play_sound()
                        windows_toast("✅ Joined Queue!", f"You joined the {server_name} queue!")
                        _notify("✅ Joined Queue!", f"You joined the {server_name} queue!")

                        # Uncheck all other queues
                        if joined_callback:
                            joined_callback(server_name)

                        # (self-ping in commands channel removed)

                    except discord.errors.HTTPException as e:
                        m = f"[{server_name}] ERROR clicking button: {e}"
                        logger.error(m); _gui_log("❌ " + m)
                    return

        m = f"[{server_name}] ERROR — No clickable button found"
        logger.error(m); _gui_log("❌ " + m)

    async def ping_self(self, channel, message_text: str):
        """Send a message mentioning yourself in a channel."""
        try:
            await channel.send(f"<@{self.user.id}> {message_text}")
        except Exception as e:
            _gui_log(f"⚠ Could not ping self: {e}")

    # ------------------------------------------------------------------
    # Position tracking
    # ------------------------------------------------------------------

    async def check_position(self, message: discord.Message, server_cfg: dict):
        server_name = server_cfg["name"]
        guild_id    = server_cfg["guild_id"]

        if not self.joined.get(guild_id):
            return

        full_text = self._full_text(message)
        username  = self.user.name.lower()
        user_id   = str(self.user.id)
        position  = None

        for line in full_text.split("\n"):
            if username in line.lower() or user_id in line:
                match = re.match(r"^\s*(\d+)[.)]\s*", line)
                if match:
                    position = int(match.group(1))
                    break

        if position is None:
            for pattern in [r"position[:\s#]+(\d+)", r"#\s*(\d+)",
                             r"you are\s+(\d+)", r"(\d+)\s*(?:st|nd|rd|th)\s+in"]:
                match = re.search(pattern, full_text.lower())
                if match:
                    position = int(match.group(1))
                    break

        if position is None:
            return

        m = f"[{server_name}] POSITION UPDATE — Position #{position}"
        logger.info(m); _gui_log("📍 " + m)

        # 1–4 → warning popup (ask if they want to leave)
        if 1 <= position <= 4:
            if not self.warned.get(guild_id):
                self.warned[guild_id] = True
                m = f"[{server_name}] WARNING — Position #{position}, getting close!"
                logger.info(m); _gui_log("⚠️ " + m)
                play_sound()
                windows_toast(f"⚠️ Position #{position}!", f"You're #{position} in {server_name} queue!")
                if warn_callback:
                    warn_callback(server_name, position)
        elif position > 4:
            self.warned[guild_id] = False

        # 11+ → auto leave
        if position >= 11:
            m = f"[{server_name}] POSITION {position} >= 11 — Sending /leave"
            logger.info(m); _gui_log("🔴 " + m)
            await self.send_leave_command(server_cfg)

    async def send_leave_command(self, server_cfg: dict):
        server_name = server_cfg["name"]
        channel     = self.get_channel(server_cfg["commands_channel_id"])

        if channel is None:
            m = f"[{server_name}] ERROR — Commands channel not found"
            logger.error(m); _gui_log("❌ " + m)
            return

        try:
            await channel.send("/leave")
            self.joined[server_cfg["guild_id"]] = False
            self.warned[server_cfg["guild_id"]] = False
            m = f"[{server_name}] LEFT QUEUE — Sent /leave"
            logger.info(m); _gui_log("🔴 " + m)
        except discord.errors.HTTPException as e:
            m = f"[{server_name}] ERROR sending /leave: {e}"
            logger.error(m); _gui_log("❌ " + m)


def run_bot(config: dict, enabled_server_ids: set):
    bot = QueueBot(config, enabled_server_ids)
    try:
        bot.run(config["token"])
    except discord.LoginFailure:
        m = "Invalid Discord token! Check your config.json"
        logger.error(m); _gui_log("❌ " + m)
    except Exception as e:
        m = f"Bot crashed: {e}"
        logger.error(m); _gui_log("❌ " + m)
