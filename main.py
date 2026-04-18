"""
HomeVal – House Price Estimator
Entry point.

Usage:
    python main.py
"""
import logging
import sys
from pathlib import Path

# Ensure project root is on sys.path when run from any working directory
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)

from ui.app import HousePriceApp


def main():
    app = HousePriceApp()
    app.mainloop()


if __name__ == "__main__":
    main()
