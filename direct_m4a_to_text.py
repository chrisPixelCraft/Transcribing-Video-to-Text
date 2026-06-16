import argparse
import sys
from pathlib import Path

import whisper


DEFAULT_MODEL = "large-v3"
DEFAULT_OUTPUT_DIR = "output"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Transcribe an M4A file directly with Whisper, without converting it to video."
    )
    parser.add_argument("input_file", help="Path to the input .m4a file")
    parser.add_argument(
        "language",
        nargs="?",
        default=None,
        help="Optional Whisper language code, e.g. zh, en, ja. Defaults to auto-detect.",
    )
    parser.add_argument(
        "output_name",
        nargs="?",
        default=None,
        help="Optional output filename. Defaults to output/<input_basename>.txt",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Whisper model to use. Default: {DEFAULT_MODEL}",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="Torch device, e.g. cuda or cpu. Defaults to Whisper auto-select.",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for output text files. Default: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Full output text file path. Overrides output_name and --output-dir.",
    )
    parser.add_argument(
        "--initial-prompt",
        default=None,
        help="Optional prompt to bias terminology or writing style.",
    )
    parser.add_argument(
        "--task",
        choices=("transcribe", "translate"),
        default="transcribe",
        help="Whisper task. Default: transcribe",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Disable Whisper verbose segment output.",
    )
    return parser.parse_args()


def resolve_output_path(args, input_path):
    if args.output:
        output_path = Path(args.output).expanduser()
    else:
        if args.output_name:
            filename = args.output_name
            if not filename.endswith(".txt"):
                filename = f"{filename}.txt"
        else:
            filename = f"{input_path.stem}.txt"
        output_path = Path(args.output_dir) / filename

    output_path = output_path.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def transcribe_m4a(args):
    input_path = Path(args.input_file).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if input_path.suffix.lower() != ".m4a":
        print(f"Warning: expected an .m4a file, got: {input_path.suffix}")

    output_path = resolve_output_path(args, input_path)

    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print(f"Model: {args.model}")
    print(f"Language: {args.language or 'auto-detect'}")

    if args.device:
        print(f"Device: {args.device}")
        model = whisper.load_model(args.model, device=args.device)
    else:
        print("Device: auto")
        model = whisper.load_model(args.model)

    options = {
        "task": args.task,
        "verbose": not args.quiet,
    }
    if args.language:
        options["language"] = args.language
    if args.initial_prompt:
        options["initial_prompt"] = args.initial_prompt
    if args.device == "cpu":
        options["fp16"] = False

    result = model.transcribe(str(input_path), **options)
    text = result.get("text", "").strip()

    output_path.write_text(text + "\n", encoding="utf-8")
    print(f"Saved transcript to: {output_path}")
    return output_path


def main():
    args = parse_args()
    try:
        transcribe_m4a(args)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
