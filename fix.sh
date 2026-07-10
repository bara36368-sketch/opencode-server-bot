cd ~/opencode-server-bot
git pull
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete
python opencode_bot.py