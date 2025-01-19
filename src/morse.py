import enum
import pathlib
import numpy as np
from scipy.io import wavfile

MORSE_CODE = { # true is short, false is long
    "e": [True],
    "a": [True, False],
    "w": [True, False, False],
    "j": [True, False, False, False],
    "1": [True, False, False, False, False],
    "'": [True, False, False, False, False, True],
    "r": [True, False, True],
    "ä": [True, False, True, False],
    "+": [True, False, True, False, True],
    "l": [True, False, True, True],
    "\"": [True, False, True, True, True],
    "é": [True, False, True, True, False],
    "u": [True, True, False],
    "ü": [True, True, False, False],
    "2": [True, True, False, False, False],
    "=": [True, True, False, True],
    "?": [True, True, False, True, False],
    "i": [True, True],
    "f": [True, True, True, False],
    "t": [False],
    "m": [False, False],
    "o": [False, False, False],
    "ö": [False, False, False, True],
    "8": [False, False, False, True, True],
    "s": [True, True, True],
    "v": [True, True, True, False],
    "3": [True, True, True, False, False],
    "ß": [True, True, True, False, False, False],
    "h": [True, True, True, True],
    "4": [True, True, True, True, False],
    "ch": [False, False, False, False],
    "5": [True, True, True, True, True],
    "n": [False, True],
    "d": [False, True, True],
    "b": [False, True, True, True],
    "6": [False, True, True, True, True],
    "x": [False, True, True, False],
    "/": [False, True, True, False, True],
    "k": [False, True, False],
    "y": [False, True, False, False],
    "(": [False, True, False, False, True],
    ")": [False, True, False, False, True, False],
    "c": [False, True, False, True],
    "g": [False, False, True],
    "z": [False, False, True, True],
    "7": [False, False, True, True, True],
    "q": [False, False, True, False],
    "ñ": [False, False, True, False, False],
    "@": [True, False, False, True, False, True],
    "9": [False, False, False, False, True],
    "0": [False, False, False, False, False],
    "irrtum": [True, True, True, True, True, True, True, True]
}

MORSE_SHORT = [True, False]
MORSE_LONG = [True, True, True, False]
MORSE_SYMBOL_STOP = [False, False]
MORSE_WORD_STOP = [False, False, False, False]

class Encoder():
    def __init__(self, wav_file: pathlib.Path, message: str, carrier: int, samplerate: int, baselength: int) -> None:
        self.wav_file: pathlib.Path = wav_file
        self.message: str = message
        self.carrier: int = carrier
        self.samplerate: int = samplerate
        self.baselength: int = baselength

    @staticmethod
    def construct(msg: str) -> list[bool]:
        return [
            bit for sym in msg for bit in (
                MORSE_WORD_STOP if sym == " " else [
                    morse_bit for s in MORSE_CODE[sym] for morse_bit in (MORSE_SHORT if s else MORSE_LONG)
                ] + MORSE_SYMBOL_STOP
            )
        ]
    def encode(self) -> int:
        morse_sequence: list[bool] = Encoder.construct(self.message)
        morse_seconds: int = 1 + int(float(len(morse_sequence)) * (float(self.baselength) / 1000.))

        t = np.linspace(0., morse_seconds, self.samplerate * morse_seconds)
        amplitude = np.iinfo(np.int16).max
        data = amplitude * np.sin(2. * np.pi * self.carrier * t)


        print(f"length of message '{self.message}' is {len(morse_sequence)}")
        print(f"length of t ' is {len(t)}")
        print(f"construction is {morse_sequence}")
        print(f"morse sequence will be {morse_seconds} seconds long")


        wavfile.write(self.wav_file, self.samplerate, data.astype(np.int16))
        return 0
