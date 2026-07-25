#!/bin/bash
# Run this on your phone to create .env
# It reads from setenv.sh (also gitignored) or prompts you

cd "$(dirname "$0")"

if [ -f "setenv.sh" ]; then
    echo "Creating .env from setenv.sh..."
    source setenv.sh
fi

if [ ! -f ".env" ]; then
    echo ""
    echo "=== Bot Setup ==="
    read -p "TELEGRAM_BOT_TOKEN: " BOT_TOKEN
    read -p "OWNER_ID: " OWNER_ID
    read -p "GROQ_KEY (or press enter to skip): " GROQ_KEY
    read -p "GEMINI_KEY (or press enter to skip): " GEMINI_KEY
    read -p "AGNES_KEY (or press enter to skip): " AGNES_KEY
    read -p "DEEPSEEK_KEY (or press enter to skip): " DEEPSEEK_KEY
    read -p "MISTRAL_KEY (or press enter to skip): " MISTRAL_KEY

    cat > .env << EOF
TELEGRAM_BOT_TOKEN=${BOT_TOKEN}
OWNER_ID=${OWNER_ID:-8585609360}
GROQ_KEY=${GROQ_KEY}
GEMINI_KEY=${GEMINI_KEY}
AGNES_KEY=${AGNES_KEY}
DEEPSEEK_KEY=${DEEPSEEK_KEY}
MISTRAL_KEY=${MISTRAL_KEY}
EOF
    echo ".env created!"
else
    echo ".env already exists."
fi

echo ""
echo "Done. Now run: python opencode_bot.py"
