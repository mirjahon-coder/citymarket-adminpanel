from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from main import app  # noqa: E402


def main():
    print("API is available at http://127.0.0.1:8000/docs")


if __name__ == "__main__":
    main()
