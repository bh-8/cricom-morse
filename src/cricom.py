import argparse
import pathlib
import sys
import traceback
import morse

parser = argparse.ArgumentParser(prog="cricom", description="CriCom Morse Encoder/Decoder")
parser.add_argument("action", type=str, choices=["encode", "decode"])
parser.add_argument("wav_file", type=str, help="wav file to encode/decode")
parser.add_argument("-m", "--message", type=str, default="sos", help="message used by the encoder, default is 'SOS'")
parser.add_argument("-c", "--carrier", type=int, default=600, help="carrier frequency in Hz, default is 600")
parser.add_argument("-s", "--samplerate", type=int, default=7119, help="sample rate in Hz, default is 7119")
parser.add_argument("-l", "--morselength", type=int, default=100, help="length of one 'dit' in ms, default is 100")
parser.add_argument("-f", "--force", action="store_true", help="enable overwriting")
args = parser.parse_args()

action_encode: bool = str(args.action).lower() == "encode"
action_decode: bool = str(args.action).lower() == "decode"
wav_file: pathlib.Path = pathlib.Path(args.wav_file).resolve()
morse_message: str | None = args.message
morse_carrier: int = args.carrier
morse_samplerate: int = args.samplerate
morse_baselength: int = args.morselength
switch_force: bool = args.force

try:
    if action_encode:
        if morse_message is None:
            raise ValueError(f"please provide a message to encode using parameter '--message' or '-m'")
        morse_message = morse_message.lower()
        if wav_file.exists() and not switch_force:
            raise FileExistsError(f"file '{wav_file}' does already exist, use '--force' or '-f' to confirm overwriting")

        print(f"encoding file '{wav_file}' using the following parameters:")
        print(f"\tcarrier frequency: {morse_carrier} Hz")
        print(f"\tsample rate: {morse_samplerate} Hz")
        print(f"\tbase length: {morse_baselength} ms")
        print(f"\tmessage: '{morse_message}'")

        morse_encoder: morse.Encoder = morse.Encoder(wav_file, morse_baselength, morse_carrier, morse_samplerate, morse_message)

        if morse_encoder.encode() == 0:
            print("done")
        else:
            raise AssertionError("encoding failed")
    elif action_decode:
        if not wav_file.exists():
            raise FileNotFoundError(f"could not access file '{wav_file}'")

        print(f"decoding file '{wav_file}' using the following parameters:")
        print(f"\tcarrier frequency: {morse_carrier} Hz")
        print(f"\tbase length: {morse_baselength} ms")

        morse_decoder: morse.Decoder = morse.Decoder(wav_file, morse_baselength, morse_carrier)

        if morse_decoder.decode() == 0:
            print("done")
            print(f"communicated message is '{morse_decoder.read_message()}'!")
        else:
            raise AssertionError("decoding failed")

except Exception as ex:
    print(f"[!] Error: {ex} [!]")
    print(traceback.format_exc())
    sys.exit(1)
sys.exit(0)
