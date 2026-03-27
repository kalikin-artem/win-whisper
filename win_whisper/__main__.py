"""Entry point: ``python -m win_whisper``."""

import json
import os

_DEFAULTS = {
    "model": "base",
    "hotkey": "f9",
    "paste_hotkey": "ctrl+v",
    "language": None,
}


def main() -> None:
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

    from win_whisper import BASE_DIR

    config_path = BASE_DIR / "config.json"
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            config = {**_DEFAULTS, **json.load(f)}
    else:
        config = dict(_DEFAULTS)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

    from win_whisper.app import App
    App(
        model_size=config["model"],
        hotkey=config["hotkey"],
        paste_hotkey=config["paste_hotkey"],
        language=config["language"],
    ).run()


if __name__ == "__main__":
    main()
