# Telegram Notifications Setup

Get notified when Claude Code stops and needs your input!

## Step 1: Create a Telegram Bot

1. Open Telegram and message [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the instructions to name your bot
4. **Copy the bot token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Step 2: Get Your Chat ID

### Option A: Using getUpdates API
1. Message your new bot on Telegram (send any message like "hello")
2. Visit this URL in your browser (replace `<YOUR_BOT_TOKEN>`):
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
3. Look for `"chat":{"id": YOUR_CHAT_ID}` in the JSON response
4. **Copy the chat ID number** (e.g., `123456789` or `-987654321` for groups)

### Option B: Using @userinfobot
1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. It will reply with your chat ID

## Step 3: Add to .env File

1. Copy `.env.example` to `.env` if you haven't already:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```bash
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   TELEGRAM_CHAT_ID=123456789
   ```

3. Make sure `.env` is in your `.gitignore` (it should be already)

## Step 4: Test It

The notification will be sent automatically when:
- Claude Code stops
- The hook decides human intervention is needed
- The decision is "allow" (not auto-continue)

You'll receive a message like:
```
🤖 Claude Code Stopped

Reason: Phase 2 complete, awaiting next phase decision
Confidence: high
Has Question: false

💬 Your input needed!
```

## Troubleshooting

### Not receiving notifications?

1. **Check the debug log:**
   ```bash
   tail -20 /tmp/stop_hook_debug.log | grep -i telegram
   ```

2. **Common issues:**
   - Bot token or chat ID still set to `your-bot-token-here` / `your-chat-id-here`
   - Forgot to message the bot first (required for it to send you messages)
   - `.env` file in wrong location (should be at project root: `/Users/mabolan/AgentProtocol/.env`)
   - Typo in token or chat ID

3. **Verify bot token:**
   ```bash
   curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe"
   ```
   Should return bot info if token is valid.

4. **Test sending a message:**
   ```bash
   curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage" \
     -d "chat_id=<YOUR_CHAT_ID>" \
     -d "text=Test message"
   ```

## Disable Notifications

To disable Telegram notifications:
1. Remove or comment out the credentials in `.env`:
   ```bash
   # TELEGRAM_BOT_TOKEN=...
   # TELEGRAM_CHAT_ID=...
   ```

The hook will continue working but won't send Telegram messages.
