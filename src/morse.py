import pathlib
import math
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
    def __init__(self, wav_file: pathlib.Path, baselength: int, carrier: int, samplerate: int, message: str) -> None:
        self.wav_file: pathlib.Path = wav_file
        self.baselength: float = float(baselength) / 1000.
        self.carrier: int = carrier
        self.samplerate: int = samplerate
        self.message: str = message
    @staticmethod
    def construct(msg: str) -> list[bool]:
        return [
            bit for sym in msg for bit in (
                MORSE_WORD_STOP if sym == " " else [
                    morse_bit for s in MORSE_CODE[sym] for morse_bit in (MORSE_SHORT if s else MORSE_LONG)
                ] + MORSE_SYMBOL_STOP
            )
        ]
    def convert(self, morse_code: list[bool]):
        d: int = int(float(self.samplerate) * self.baselength) # Anzahl samples pro Wahrheitswert
        t: np.ndarray = np.linspace(0., self.baselength, d, endpoint=False)
        signal: list = []
        for m in morse_code:
            if m:
                signal.extend(np.sin(2 * np.pi * self.carrier * t))
            else:
                signal.extend(np.zeros(d))
        return np.array(signal, dtype=np.float32)
    def encode(self) -> int:
        wavfile.write(self.wav_file, self.samplerate, self.convert(Encoder.construct(self.message)))
        return 0

class Decoder():
    def __init__(self, wav_file: pathlib.Path, baselength: int, carrier: int) -> None:
        self.wav_file: pathlib.Path = wav_file
        self.baselength: float = float(baselength) / 1000.
        self.carrier: int = carrier
        self.samplerate: int = None
        self.message: str = None
    @staticmethod
    def morse_invert(morse_symbol: list[bool]) -> str:
        for k, v in MORSE_CODE.items():
            if morse_symbol == v:
                return k
        return " "
    @staticmethod
    def deconstruct(morse_code: list[bool]) -> str:
        i: int = 0
        current_morse_symbol: list[bool] = []
        message: str = ""
        while i < len(morse_code):
            if morse_code[i]:
                if i + 4 < len(morse_code) and morse_code[i:i + 4] == MORSE_LONG:
                    current_morse_symbol.append(False)
                    i = i + 4
                    continue
                if i + 2 < len(morse_code) and morse_code[i:i + 2] == MORSE_SHORT:
                    current_morse_symbol.append(True)
                    i = i + 2
                    continue
                raise ValueError("failed to deconstruct morse code (1)")
            else:
                if morse_code[i:i + 4] == MORSE_WORD_STOP:
                    i = i + 4
                    message = message + Decoder.morse_invert(current_morse_symbol) + " "
                    current_morse_symbol = []
                    continue
                if morse_code[i:i + 2] == MORSE_SYMBOL_STOP:
                    i = i + 2
                    message = message + Decoder.morse_invert(current_morse_symbol)
                    current_morse_symbol = []
                    continue
                if morse_code[i] == False:
                    i = i + 1
                    continue
                raise ValueError("failed to deconstruct morse code (2)")
        return message
    @staticmethod
    def find_next_beep(signal: np.ndarray, offset: int) -> int:
        r: int = offset
        for i in range(len(signal[offset:-1])):
            if signal[i] > 0.48 and signal[i+1] > signal[i]:
                return r + i
        return -1
    def convert(self, signal: np.ndarray) -> list[bool]:
        d: int = int(float(self.samplerate) * self.baselength) # Anzahl samples pro Wahrheitswert
        t: np.ndarray = np.linspace(0., self.baselength, d, endpoint=False)
        beep_signal: np.ndarray = np.roll(np.sin(2 * np.pi * self.carrier * t), -1)

        signal /= np.max(np.abs(signal), axis=0)

        i: int = Decoder.find_next_beep(signal, 0)
        if i == -1:
            raise AssertionError("could not find beep sequence in audio file")

        morse_code: list[bool] = []
        while len(signal) - i >= d:
            dit: np.ndarray = signal[i:i + d]
            beep_phase: int = Decoder.find_next_beep(dit, 0)
            morse_code.append(False if beep_phase == -1 or beep_phase > (d / 2) else bool((sum([abs(x) for x in np.subtract(beep_signal, np.roll(dit, -beep_phase))]) / d) < 0.6))
            i = i + d

        return morse_code

    def decode(self) -> int:
        self.samplerate, wav_data = wavfile.read(self.wav_file)
        self.message = Decoder.deconstruct(self.convert(wav_data))

        return 0 if self.message is not None and len(self.message) > 0 else 1
    def read_message(self) -> str | None:
        return self.message
