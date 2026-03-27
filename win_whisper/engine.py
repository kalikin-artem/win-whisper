"""Model loading, audio recording, and transcription."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

import numpy as np
import sounddevice as sd

from .log import log

if TYPE_CHECKING:
    from faster_whisper import WhisperModel

SAMPLE_RATE = 16_000
BLOCK_SIZE = 1_024
MIN_SECONDS = 0.4


class Engine:
    def __init__(self) -> None:
        self.model: WhisperModel | None = None

    def load(self, model_size: str) -> None:
        from faster_whisper import WhisperModel

        log.info("Loading '%s'...", model_size)
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        log.info("Model ready.")

    def record(self, stop: threading.Event) -> np.ndarray | None:
        chunks: list[np.ndarray] = []
        with sd.InputStream(
            samplerate=SAMPLE_RATE, channels=1,
            dtype="float32", blocksize=BLOCK_SIZE,
        ) as stream:
            while not stop.is_set():
                data, _ = stream.read(BLOCK_SIZE)
                chunks.append(data.copy())

        if not chunks:
            return None

        audio = np.concatenate(chunks).flatten()
        duration = len(audio) / SAMPLE_RATE
        log.info("Captured %.2fs", duration)
        return audio if duration >= MIN_SECONDS else None

    def transcribe(self, audio: np.ndarray, *, language: str | None = None) -> str:
        segments, info = self.model.transcribe(
            audio,
            language=language,
            beam_size=1,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500, "speech_pad_ms": 200},
        )
        text = " ".join(seg.text.strip() for seg in segments).strip()
        log.info("[%s] %r", info.language, text)
        return text
