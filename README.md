# MCTiers Auto Queue Bot
**Educational selfbot — only use with explicit server owner permission.**

---

## Files
```
mctiers_bot/
├── gui.py           ← Run this! The startup window with checkboxes
├── bot.py           ← Core selfbot logic
├── logger.py        ← Logging to console + /logs folder
├── config.json      ← Your server settings (edit this first!)
├── start_bot.bat    ← Double-click to launch on Windows startup
└── logs/            ← Auto-created. One log file per day.
```

---

## 1. Install Python & dependency

1. Download Python 3.10+ from https://python.org
2. Open a terminal and run:
```
pip install discord.py-self
```

---

## 2. Edit config.json

Fill in these fields for **each** server:

| Field | How to get it |
|-------|--------------|
| `token` | F12 in Discord browser → Network tab → any request → `Authorization` header |
| `guild_id` | Right-click server icon → Copy Server ID |
| `queue_channel_id` | Right-click queue channel → Copy Channel ID |
| `queue_message_id` | Right-click queue status message → Copy Message ID |
| `commands_channel_id` | Right-click commands channel → Copy Channel ID |

> Enable **Developer Mode** first: Discord Settings → Advanced → Developer Mode ✓

Update `queue_open_keywords` to match the **exact words** MCTiers uses when
the queue opens (e.g. `"queue is now available"`).

---

## 3. Run the bot

**Double-click `gui.py`** or run:
```
python gui.py
```

A window appears showing all your servers with toggles:
- **AUTO-JOIN** (green) = bot will watch AND join the queue
- **LOG ONLY** (grey) = bot watches and logs but won't click join

Click **▶ START BOT**. Your selections are saved for next time.

---

## 4. Auto-start on Windows boot

1. Press `Win + R` → type `shell:startup` → hit Enter
2. Create a shortcut to `start_bot.bat` in that folder
3. Now the bot launches every time you start your PC!

---

## 5. Reading the logs

Logs are saved to `/logs/queue_YYYY-MM-DD.log`. Each entry looks like:

```
[14:32:01] [INFO] [MCTiers Main] QUEUE OPEN DETECTED
[14:32:01] [INFO] [MCTiers Main] Waiting 0.5s then clicking join...
[14:32:02] [INFO] [MCTiers Main] JOINED QUEUE | Clicked button: 'Join Queue'
[14:32:45] [INFO] [MCTiers Main] POSITION UPDATE | Position #11
[14:32:45] [INFO] [MCTiers Main] POSITION 11 >= 10 — Sending /leave
[14:32:45] [INFO] [MCTiers Main] LEFT QUEUE | Sent /leave to commands channel
```

---

## Troubleshooting

**Bot doesn't detect queue opening**
→ Check `queue_open_keywords` in config.json matches exactly what the message says

**Button click fails**
→ The queue message might use a slash command instead of a button — let me know and I'll adapt the bot

**Position not detected**
→ The bot tries several patterns like "Position: 12", "#12", "12th in queue"
→ If MCTiers uses different wording, open `bot.py` and add a pattern to the `patterns` list in `check_position()`

**Token invalid**
→ Re-copy your token; they expire if you change your password

**All made by AI - Claude**
