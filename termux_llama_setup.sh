#!/data/data/com.termux/files/usr/bin/bash
# Termux llama.cpp + Qwen2.5-3B setup for OpenCode Bot
# Run this on your phone in Termux

set -e

echo "=== Installing dependencies ==="
pkg update -y
pkg upgrade -y
pkg install -y git cmake python ninja build-essential

echo "=== Cloning llama.cpp ==="
cd ~
rm -rf llama.cpp
git clone --depth 1 https://github.com/ggml-ai/llama.cpp
cd llama.cpp

echo "=== Building (this takes a few minutes) ==="
mkdir -p build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DLLAMA_CUDA=OFF -DLLAMA_METAL=OFF
cmake --build . --config Release -- -j4

echo "=== Installing Python server deps ==="
pip install fastapi uvicorn sse-starlette pydantic-settings

echo "=== Downloading Qwen2.5-3B-Instruct Q4_K_M ==="
cd ~
mkdir -p models
curl -L -o models/qwen2.5-3b-instruct-q4.gguf \
  https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf

echo "=== Creating run script ==="
cat > ~/run_llm.sh << 'SCRIPT'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/llama.cpp/build
./bin/llama-server \
  -m ~/models/qwen2.5-3b-instruct-q4.gguf \
  --host 127.0.0.1 \
  --port 8080 \
  --n-gpu-layers 0 \
  --ctx-size 4096 \
  --threads 4
SCRIPT
chmod +x ~/run_llm.sh

echo ""
echo "=== DONE ==="
echo ""
echo "To start the LLM server:"
echo "  tmux new-session -s llm '~/run_llm.sh'"
echo ""
echo "Then use /ai local or /ai local-qwen3b in the bot"
echo ""
echo "To keep it running 24/7, add to crontab or use a Termux:Boot script."
