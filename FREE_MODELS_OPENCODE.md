# Free Models for Opencode (Higher-Tier Than Big Pickle)

> **Current setup:** this machine runs opencode on `opencode/big-pickle` (rated 4/5 free in OpenCode Zen). Below are **free** models rated higher or playing in a higher league, how to enable each in opencode, and what this specific machine already has configured.
>
> Sources researched: opencode.ai docs (Jul 2026), OpenCode Zen free-model review (bswen, Apr 2026), OpenRouter free-models collection (Jul 2026), free-LLM API guides (2026).

---

## 1. Quick verdict

| Tier | Free model | Rating vs big-pickle | Cost | Privacy |
|---|---|---|---|---|
| **Best free upgrade** | `opencode/gpt-5-nano` (OpenCode Zen) | 5/5 vs 4/5 | $0, **permanently free** | Data **not** used for training |
| **Same tier, complex tasks** | `opencode/qwen3.6-plus-free` | 4/5 (stronger on refactor/architecture) | $0, limited-time | Data may train |
| **Frontier via free sub** | `github/claude-sonnet-3-5` (GitHub Copilot free) | Frontier-class | $0 | Cloud |
| **Frontier via free API** | `google/gemini-2.5-flash` | Frontier-class | $0, ~1,500 req/day | Cloud (trains on free tier) |
| **Speed king** | `groq/llama-3.3-70b-versatile` | Very high, ~500 t/s | $0 | Cloud |

Rule of thumb from the community review:
- Daily / privacy-sensitive work -> **GPT 5 Nano** (only free model that guarantees data is never stored or trained on).
- Complex refactors / architecture on non-sensitive code -> **big-pickle** or **Qwen3.6 Plus Free**.
- Anything bigger (repo-scale, 8B-class reasoning) -> free-tier **Gemini 2.5 Flash**, **Groq Llama 3.3 70B**, or **OpenRouter `:free`** frontier models.

---

## 2. OpenCode Zen built-in free models

Enable with `/connect` -> "OpenCode Zen", then pick with `/models`. All use the `opencode/` provider prefix.

| Model ID (provider/model) | Rating | Status | Best for |
|---|---|---|---|
| `opencode/gpt-5-nano` | 5/5 | **Permanently free** | Lightweight tasks, privacy-first, default daily driver |
| `opencode/big-pickle` | 4/5 | Limited-time free | Complex programming, code review (current default) |
| `opencode/qwen3.6-plus-free` | 4/5 | Limited-time free | Complex tasks, non-sensitive projects |
| `opencode/nemotron-3-super-free` | 3/5 | Limited-time free | Code generation, daily coding |
| `opencode/minimax-m2.5-free` | 3/5 | Limited-time free | Learning, exploration |

Set as default in `opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode/gpt-5-nano"
}
```

---

## 3. Free frontier models via connected providers

### Google Gemini (frontier, 1M-token context)
Free tier ~1,500 req/day (some tiers 250/day), no credit card.

1. Get a key: <https://aistudio.google.com/apikey>
2. Add to `~/.config/opencode/.env`:

```
GOOGLE_API_KEY=your_key_here
```

3. Use `google/gemini-2.5-flash` (or a 2.0/2.5 variant). 1M-token context makes it the only real free option for whole-codebase questions without RAG.

### Groq (free, fastest inference)
Llama 3.3 70B at ~500 t/s. Key already present on this machine.

```json
{ "provider": { "groq": { "apiKey": "gsk_..." } } }
```

Use: `groq/llama-3.3-70b-versatile` (Llama 70B ~30 req/min, 1,000 req/day). Smaller 8B models are even more generous (~14,000 req/day).

### OpenRouter `:free` models (aggregator, one key)
Key already present on this machine. Free models on the collection (Jul 2026):

| Model ID | Why |
|---|---|
| `openrouter/meta-llama/llama-3.3-70b-instruct:free` | Best overall free |
| `openrouter/deepseek/deepseek-r1:free` | Best reasoning |
| `openrouter/mistral/devstral-2:free` | Best for coding |
| `openrouter/google/gemma-3-27b-it:free` | Google's free 27B |
| `openrouter/openrouter/auto` | Auto-picks best available free model |

### GitHub Copilot (free tier -> frontier Claude)
`github/claude-sonnet-3-5` is Claude-class and $0 when Copilot is enabled (free for verified students via <https://github.com/settings/education/benefits>). In the TUI: `/connect` -> GitHub -> authenticate in browser.

### NVIDIA NIM (free API key already configured on this machine)
`nvidia/nvidia/nemotron-3-ultra-550b-a55b` (550B) is already wired into this machine's subagents (reasoner, reviewer, researcher, security, etc.). Frontier-scale and free with an NVIDIA Build/API key.

### Kilo AI free gateway (plugin)
Community plugin exposes Kilo's free gateway in opencode: `minimax/minimax-m2.5:free`, `z-ai/glm-5:free`, `arcee-ai/trinity-large-preview:free`, `qwen/qwen3-235b-a22b-thinking-2507`, `stepfun/step-3.5-flash:free`.
Install: `irm https://raw.githubusercontent.com/ang-or-five/opencode-kilo-free-provider/refs/heads/main/install.py | python` (Windows).

---

## 4. What THIS machine already has (keys in `~/.config/opencode/opencode.json`)

| Provider | Key | Free models available right now |
|---|---|---|
| OpenRouter | `sk-or-...` (set) | All `:free` models incl. DeepSeek-R1, Llama 3.3 70B, Gemma 3 27B |
| Groq | `gsk_...` (set) | Llama 3.3 70B / 8B free |
| NVIDIA | `nvapi-...` (set) | Nemotron 3 Ultra 550B, Llama 3.3 70B |

Only missing for the full free lineup: **Google** (`GOOGLE_API_KEY`) and optionally **GitHub Copilot** (`/connect`).

---

## 5. How to switch (TUI)

1. `/connect` -> OpenCode Zen (or add provider keys above).
2. `/models` -> pick the free model.
3. Or set the default in `opencode.json` (`"model": "opencode/gpt-5-nano"`).
4. Check usage anytime: `opencode stats`.

To run a one-off session on a higher-tier free model:

```bash
opencode tui --model opencode/gpt-5-nano
opencode tui --model google/gemini-2.5-flash
opencode tui --model openrouter/deepseek/deepseek-r1:free
```

---

## 6. Gotchas

- **Free != private**: most free tiers train on your data (Gemini free tier, big-pickle, Qwen free). GPT 5 Nano is the exception. Don't paste proprietary/secret code into the promotional free models.
- **Rate limits**: Groq 70B ~30 req/min; Gemini ~15 req/min, 1,500/day. On 429, wait or fall back to another provider.
- **Ephemeral**: "limited-time free" models (big-pickle, Qwen3.6 Plus, Nemotron 3) can vanish or become paid. Have a backup free model (GPT 5 Nano) for critical work.
