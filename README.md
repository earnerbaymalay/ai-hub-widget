# ⬡ AI Hub Widget v5

> **A clean, solid desktop sidebar for launching and monitoring multiple AI tools — Claude, Kimi, Gemini, Qwen, Codex, Kilo Code, and Ollama.**

![Version](https://img.shields.io/badge/version-5.0-blue?style=flat-square)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen?style=flat-square)
![Windows](https://img.shields.io/badge/platform-Windows%2010%2F11-lightgrey?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-orange?style=flat-square)

---

## ✨ Features

| Feature | Details |
|---------|---------|
| 🎨 **Solid UI** | Zero transparency — always readable, no bleed-through |
| 🤖 **7 AI Tools** | Claude · Kimi · Gemini · Qwen · Codex · Kilo Code · Ollama |
| 🟢 **Live Session Dots** | Green dot next to any AI tool that's actively running |
| 📊 **System Monitor** | Real-time CPU, RAM, disk, and actual network KB/s (via psutil) |
| 🎨 **3 Themes** | Dark · Light · Midnight — switcher in header, applies instantly |
| 📜 **Prompt Templates** | 15+ templates across Dev, Analysis, Creative, and System categories |
| ⌨️ **Command Center** | Type a prompt, pick your AI, hit Enter — launches in a terminal tab |
| 🖱️ **Drag & Resize** | Drag the header to move; resize from corners |
| 💾 **Persistent Config** | Position, size, theme, and last-used AI saved across restarts |
| 🔒 **Single Instance** | Socket lock prevents duplicate widget windows |

---

## 🖼️ Layout

```
┌─ ⬡ AI Hub  v5 ─────────── [dark ▾] [─] [×] ─┐
├── SYSTEM ──────────────────────────────────────┤
│  CPU  ████████░░░░░░░░  42 %                   │
│  RAM  █████████████░░░  67 %                   │
│  C:   ████████████░░    73%                    │
│  D:   █████░░░░░░░░░░   41%                    │
│  ▼ 2.1 KB/s    ▲ 0.4 KB/s   ⏱ 2d 4h 12m      │
├── AI TOOLS ────────────────────────────────────┤
│ ▌◉ Claude ●  ▌◈ Kimi ○    ▌◆ Gemini ○        │
│   Anthropic     Moonshot     Google            │
│ ▌◇ Qwen ○    ▌▣ Codex ○   ▌▲ Kilo ●          │
│   Alibaba       OpenAI        Kilo Code        │
│ ▌◎ Ollama ○                                   │
│   Local LLMs                                   │
├── COMMAND ─────────────────────────────────────┤
│ ▶  Claude                                      │
│ [________________________________] [▶]         │
│ [📋 Paste] [🗑 Clear]                          │
├── TEMPLATES ───────────────────────────────────┤
│ [💻 Dev] [📊 Analysis] [✨ Creative] [⚙️ System]│
├── OUTPUT ──────────────────── [📋 Copy] [🗑] ──┤
│ AI Hub v5 ready.                               │
│ Select a tool above, enter a prompt...         │
└──────────────────────────── 09:41:32 ─ Ready ─┘
```

---

## 📋 Requirements

- **Python** 3.8 or newer
- **Windows** 10 or 11
- **Packages:** `psutil`, `WMI`

---

## 🚀 Install

```powershell
# 1. Clone the repo
git clone https://github.com/pat21/ai-hub-widget.git
cd ai-hub-widget

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch
python ai_widget_v5.py
```

---

## 🔁 Autostart on Login

To have the widget launch silently when Windows starts:

```powershell
$startup = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
Copy-Item autostart.vbs $startup
```

Or run `launch.bat` manually anytime.

---

## 🎨 Themes

Switch themes from the dropdown in the header. Widget restarts in ~0.6s to apply.

| Theme | Description |
|-------|-------------|
| `dark` | VS Code dark — deep grey, blue accent |
| `light` | Clean white, high contrast |
| `midnight` | Deep navy with purple accent and teal highlights |

---

## 🤖 AI Tools

| Tool | Command | Key | Color |
|------|---------|-----|-------|
| Claude | `claude` | `c` | 🟠 |
| Kimi | `kimi` | `k` | 🩵 |
| Gemini | `gemini` | `g` | 🔵 |
| Qwen | `qwen` | `q` | 🟣 |
| Codex | `codex` | `cx` | 🟢 |
| **Kilo Code** | `kilo` | `kc` | 💗 |
| Ollama | `ollama run ...` | `o` | 🔴 |

To add a new tool, edit the `AI_TOOLS` dict at the top of `ai_widget_v5.py`.

---

## ⚙️ Config

Saved automatically to `~/.ai-hub-v5-config.json`:

```json
{
  "position": {"x": 50, "y": 50},
  "size": {"width": 380, "height": 720},
  "always_on_top": true,
  "theme": "dark",
  "selected_ai": "Claude"
}
```

---

## 📁 Files

```
ai-hub-widget/
├── ai_widget_v5.py   ← Main application (current)
├── ai_widget_v4.py   ← Previous version (archived)
├── launch.bat        ← Quick launch
├── autostart.vbs     ← Silent Windows startup
├── requirements.txt  ← pip dependencies
└── README.md
```

---

## 🛠️ Troubleshooting

| Issue | Fix |
|-------|-----|
| "Python not found" | Install Python 3.8+ from python.org, add to PATH |
| "No module named wmi" | `pip install WMI` |
| "No module named psutil" | `pip install psutil` |
| Widget already running | Check Task Manager for `pythonw.exe` |
| Position lost after move | Delete `~/.ai-hub-v5-config.json` to reset |

---

## 🔄 Changelog

### v5.0 — Current
- Complete visual redesign: solid background, VS Code sidebar aesthetic
- Zero transparency — always readable
- Active session detection (live green dots)
- Real network stats via psutil (actual KB/s)
- Mousewheel scroll only within scroll canvas (no conflict with terminal)
- Midnight theme added
- Kilo Code included in all views

### v4.0
- Fluent Design aesthetics, scrollable content, 25+ templates

---

## 📄 License

MIT — use freely, credit appreciated.
