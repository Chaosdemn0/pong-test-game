"""Retro-style generated sound effects for the Pong project."""
from __future__ import annotations

import math
import struct

SAMPLE_RATE = 44100


def _make_pcm16(
    frequency: float,
    duration: float,
    volume: float = 0.3,
    sweep: float = 0.0,
    body_ratio: float = 0.18,
) -> bytes:
    frame_count = max(1, int(SAMPLE_RATE * duration))
    samples = bytearray()

    for index in range(frame_count):
        time = index / SAMPLE_RATE
        progress = min(1.0, time / max(duration, 1e-6))
        current_frequency = frequency * (1.0 + sweep * time)
        phase = 2 * math.pi * current_frequency * time
        wave = math.sin(phase)
        wave += 0.2 * math.sin(phase * 2 + 0.35)
        wave += body_ratio * math.sin(phase * 0.5)

        attack = min(1.0, time / min(0.012, duration / 3))
        release = min(1.0, (duration - time) / min(0.045, duration / 3))
        envelope = attack * release * math.exp(-4.0 * progress)
        amplitude = volume * envelope
        sample_value = int(max(-1.0, min(1.0, wave * amplitude)) * 32767)
        samples.extend(struct.pack("<h", sample_value))

    return bytes(samples)


def _wrap_wav(audio: bytes) -> bytes:
    frame_count = len(audio) // 2
    byte_rate = SAMPLE_RATE * 2
    block_align = 2
    data_size = len(audio)
    riff_size = 36 + data_size
    header = (
        b"RIFF"
        + struct.pack("<I", riff_size)
        + b"WAVE"
        + b"fmt "
        + struct.pack("<IHHIIHH", 16, 1, 1, SAMPLE_RATE, byte_rate, block_align, 16)
        + b"data"
        + struct.pack("<I", data_size)
    )
    return header + audio


def build_retro_sfx() -> dict[str, bytes]:
    return {
        "paddle": _wrap_wav(_make_pcm16(230.0, 0.10, 0.24, sweep=0.12, body_ratio=0.24)),
        "wall": _wrap_wav(_make_pcm16(165.0, 0.085, 0.21, sweep=0.10, body_ratio=0.28)),
        "score": _wrap_wav(_make_pcm16(420.0, 0.20, 0.34, sweep=0.16, body_ratio=0.20)),
        "menu": _wrap_wav(_make_pcm16(280.0, 0.12, 0.25, sweep=0.12, body_ratio=0.22)),
    }
