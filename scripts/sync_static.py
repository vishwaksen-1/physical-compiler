"""Mirror the Phase 0 static frontend from web/ into Vercel's public/ dir."""

from pathlib import Path
from shutil import copytree, rmtree


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "web"
TARGET = ROOT / "public"


def main() -> None:
    if TARGET.exists():
        rmtree(TARGET)

    copytree(SOURCE, TARGET)
    print(f"Synced {SOURCE.relative_to(ROOT)}/ -> {TARGET.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
