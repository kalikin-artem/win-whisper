<p align="center">
  <img src="icons/icon_256.png" width="128" alt="Win Whisper">
</p>

<h1 align="center">Win Whisper</h1>

<p align="center">
  🎙️ Local, offline voice-to-text for Windows<br>
  Hold a key, speak, release — text appears wherever you type
</p>

<p align="center">
  <a href="https://github.com/kalikin-artem/win-whisper/releases">⬇️ Download</a>&nbsp;&nbsp;·&nbsp;&nbsp;
  <a href="#how-it-works">How it works</a>&nbsp;&nbsp;·&nbsp;&nbsp;
  <a href="#-configuration">Configuration</a>&nbsp;&nbsp;·&nbsp;&nbsp;
  <a href="#-models">Models</a>
</p>

---

## ⬇️ Getting started

1. Download **win-whisper.exe** from the [latest release](https://github.com/kalikin-artem/win-whisper/releases)
2. Run it — a small icon appears in your system tray
3. Wait for the **"Ready"** notification (first launch downloads the model, ~145 MB)

That's it. No installation, no Python, no setup. Works fully offline after the first run.

## How it works

1. 🟢 **Hold F9** — recording starts
2. 🎤 **Speak** — say anything in any language
3. 🔴 **Release F9** — text is transcribed and pasted into the active window

> 💡 Right-click the tray icon to switch models, reload, or exit.

## ⚙️ Configuration

On first run, a `config.json` file is created next to the executable:

```json
{
  "model": "base",
  "hotkey": "f9",
  "paste_hotkey": "ctrl+v",
  "language": null
}
```

| Option         | Description                                                                | Default    |
| -------------- | -------------------------------------------------------------------------- | ---------- |
| `model`        | Whisper model size — see [Models](#-models) below                          | `"base"`   |
| `hotkey`       | Key to hold while speaking                                                 | `"f9"`     |
| `paste_hotkey` | Key combination used to paste the text                                     | `"ctrl+v"` |
| `language`     | Force a specific language (`"en"`, `"ua"`, etc.) or `null` for auto-detect | `null`     |

Edit the file and restart the app to apply changes.

## 🧠 Models

All models auto-detect the language (90+ supported).

| Model    | Download size | Speed  | Accuracy |
| -------- | :-----------: | :----: | :------: |
| `tiny`   |     75 MB     | ⚡⚡⚡ |   ★☆☆    |
| `base`   |    145 MB     |  ⚡⚡  |   ★★☆    |
| `small`  |    240 MB     |   ⚡   |   ★★★    |
| `medium` |    770 MB     |   🐢   |   ★★★★   |

You can also switch models from the tray icon menu without editing the config.

Powered by [Faster Whisper](https://github.com/SYSTRAN/faster-whisper) (CTranslate2, runs on CPU).

## 🛠️ Run from source

```bash
pip install .
win-whisper
```

Or without installing:

```bash
pip install -r requirements.txt
python -m win_whisper
```

Requires Python 3.10+ and Windows 10/11.

## ❓ Troubleshooting

| Problem               | Fix                                                                                       |
| --------------------- | ----------------------------------------------------------------------------------------- |
| Nothing happens       | Check `win-whisper.log` next to the executable                                            |
| "No speech"           | Speak louder or hold longer. Check your default mic in Windows Sound settings             |
| Want GPU acceleration | In `config.json` this isn't available yet — see `win_whisper/engine.py` to switch to CUDA |

## 📄 License

MIT — [Artem Kalikin](mailto:artem@kalikin.org)
