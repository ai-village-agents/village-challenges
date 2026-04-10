import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 2:
        print("Final score: 0/100")
        return

    secret_path = Path(__file__).resolve().parent / "secret.txt"
    try:
        secret_phrase = secret_path.read_text(encoding="utf-8").strip()
    except (FileNotFoundError, OSError):
        print("Final score: 0/100")
        return

    submission_dir = Path(sys.argv[1])
    score = 0

    if (submission_dir / "url.txt").exists():
        score += 25

    if (submission_dir / "downloaded_file.zip").exists():
        score += 50

    submission_file = submission_dir / "submission.txt"
    try:
        submission_contents = submission_file.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        submission_contents = ""

    if secret_phrase and submission_contents and secret_phrase in submission_contents:
        score += 100

    print(f"Final score: {score}/100")


if __name__ == "__main__":
    main()
