"""Retro-style generated sound effects for the Pong project."""
from __future__ import annotations

import math
import struct

SAMPLE_RATE = 22050


def _make_pcm16(frequency: float, duration: float, volume: float = 0.3, sweep: float = 0.0) -> bytes:
    frame_count = max(1, int(SAMPLE_RATE * duration))
    samples = bytearray()

    for index in range(frame_count):
        time = index / SAMPLE_RATE
        current_frequency = frequency * (1.0 + sweep * time)
        wave = math.sin(2 * math.pi * current_frequency * time)
        wave += 0.35 * math.sin(2 * math.pi * current_frequency * 2 * time + 0.8)

        attack = min(0.04, duration * 0.35)
        release = min(0.12, duration * 0.5)
        if time < attack:
            envelope = time / attack
        elif duration - time < release:
            envelope = max(0.0, (duration - time) / release)
        else:
            envelope = 1.0

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
        "paddle": _wrap_wav(_make_pcm16(540.0, 0.09, 0.28, sweep=0.15)),
        "wall": _wrap_wav(_make_pcm16(260.0, 0.06, 0.22, sweep=0.08)),
        "score": _wrap_wav(_make_pcm16(620.0, 0.20, 0.52, sweep=0.32)),
        "menu": _wrap_wav(_make_pcm16(440.0, 0.11, 0.30, sweep=0.18)),
    }


def build_retro_music() -> bytes:
    lead = [
        (220.0, 0.25),
        (220.0, 0.25),
        (246.94, 0.25),
        (293.66, 0.5),
        (293.66, 0.25),
        (246.94, 0.25),
        (220.0, 0.25),
        (196.0, 0.5),
        (196.0, 0.25),
        (220.0, 0.25),
        (246.94, 0.25),
        (293.66, 0.5),
        (330.0, 0.25),
        (293.66, 0.25),
        (246.94, 0.25),
        (220.0, 0.75),
    ]
    bass = [
        (55.0, 0.5),
        (55.0, 0.5),
        (61.74, 0.5),
        (73.42, 0.5),
        (73.42, 0.5),
        (61.74, 0.5),
        (55.0, 0.5),
        (46.25, 0.5),
        (46.25, 0.5),
        (55.0, 0.5),
        (61.74, 0.5),
        (73.42, 0.5),
        (82.41, 0.5),
        (73.42, 0.5),
        (61.74, 0.5),
        (55.0, 0.75),
    ]
    drums = [
        (90.0, 0.1),
        (45.0, 0.08),
        (90.0, 0.1),
        (45.0, 0.08),
        (90.0, 0.1),
        (45.0, 0.08),
        (90.0, 0.1),
        (45.0, 0.08),
        (90.0, 0.1),
        (45.0, 0.08),
        (90.0, 0.1),
        (45.0, 0.08),
        (90.0, 0.1),
        (45.0, 0.08),
        (90.0, 0.1),
        (45.0, 0.08),
    ]
    samples = bytearray()
    for index, (note, duration) in enumerate(lead):
        samples.extend(_make_pcm16(note, duration, 0.16, sweep=0.08))
        samples.extend(_make_pcm16(note / 2, duration * 0.55, 0.06, sweep=0.03))
        bass_note, bass_duration = bass[index]
        samples.extend(_make_pcm16(bass_note, min(duration, bass_duration), 0.12, sweep=0.02))
        drum_freq, drum_duration = drums[index]
        samples.extend(_make_pcm16(drum_freq, drum_duration, 0.10, sweep=0.0))
    return _wrap_wav(bytes(samples))
