#!/data/data/com.termux/files/usr/bin/bash
# OpenCode Bot — Environment Variables
# Fill in your real API keys below, then run: source setenv.sh
# Add to ~/.bashrc to auto-load: echo "source ~/opencode-server-bot/setenv.sh" >> ~/.bashrc

export TELEGRAM_BOT_TOKEN="8839361042:AAGqZQv0D18kdvpWXgC5PZpiihKW3SsboEA"
export OWNER_ID="8585609360"

# AI Provider Keys (at least one needed)
export GROQ_KEY="gsk_your_groq_key_here"
export GEMINI_KEY="AIzaSy_your_gemini_key_here"
export OPENROUTER_KEY="sk-or-your_openrouter_key_here"
export DEEPSEEK_KEY="sk_your_deepseek_key_here"
export MISTRAL_KEY="your_mistral_key_here"
export SAMBANOVA_KEY="your_sambanova_key_here"
export CEREBRAS_KEY="csk_your_cerebras_key_here"
export GITHUB_KEY="your_github_token_here"
export NVIDIA_KEY="nvapi-your_nvidia_key_here"
export TOGETHER_KEY="tgp_v1_your_together_key_here"
export FIREWORKS_KEY="fw_your_fireworks_key_here"
export COHERE_KEY="your_cohere_key_here"
export XAI_KEY="xai_your_xai_key_here"
export LEPTON_KEY="your_lepton_key_here"

echo "✓ OpenCode Bot environment variables loaded"
echo "  Bot token: ${TELEGRAM_BOT_TOKEN:0:8}..."
echo "  Owner ID: $OWNER_ID"
echo "  Providers: groq gemini openrouter deepseek mistral sambanova cerebras github nvidia together fireworks cohere xai lepton"
