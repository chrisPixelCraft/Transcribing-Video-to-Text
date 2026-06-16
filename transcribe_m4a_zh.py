import argparse
from pathlib import Path

import whisper


DEFAULT_MODEL = "large-v3"
DEFAULT_LANGUAGE = "zh"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Transcribe an M4A file to Chinese text with Whisper large-v3."
    )
    parser.add_argument("input_file", help="Path to the input .m4a file")
    parser.add_argument(
        "-o",
        "--output",
        help="Output text file path. Defaults to output/<input_basename>.txt",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Whisper model to use. Default: {DEFAULT_MODEL}",
    )
    parser.add_argument(
        "--language",
        default=DEFAULT_LANGUAGE,
        help=f"Language code hint for Whisper. Default: {DEFAULT_LANGUAGE}",
    )
    parser.add_argument(
        "--device",
        default="cuda",
        help="Torch device, e.g. cpu or cuda. Default: Whisper auto-selects.",
    )
    parser.add_argument(
        "--initial-prompt",
        default=None,
        help="Optional prompt to bias terminology or writing style.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    input_path = Path(args.input_file).expanduser().resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if input_path.suffix.lower() != ".m4a":
        print(f"Warning: expected an .m4a file, got: {input_path.suffix}")

    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = Path("output").resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{input_path.stem}.txt"

    print(f"Loading Whisper model: {args.model}")
    if args.device:
        model = whisper.load_model(args.model, device=args.device)
    else:
        model = whisper.load_model(args.model)

    print(f"Transcribing: {input_path}")
    print(f"Language hint: {args.language}")

    transcribe_options = {
        "language": args.language,
        "task": "transcribe",
        "verbose": True,
    }
    if args.initial_prompt:
        transcribe_options["initial_prompt"] = args.initial_prompt

    result = model.transcribe(str(input_path), **transcribe_options)

    with output_path.open("w", encoding="utf-8") as f:
        f.write(result["text"].strip() + "\n")

    print(f"Saved transcript to: {output_path}")


if __name__ == "__main__":
    main()
