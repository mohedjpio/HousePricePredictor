"""
Application configuration and constants.
"""
from pathlib import Path

BASE_DIR   = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
MODELS_DIR = BASE_DIR / "models"

DATA_PATH  = ASSETS_DIR / "egypt_housing_clean.csv"
MODEL_PATH = MODELS_DIR / "housing_model.pkl"

MODEL_PARAMS = {
    "n_estimators":   400,
    "learning_rate":  0.05,
    "max_depth":      5,
    "subsample":      0.8,
    "min_samples_leaf": 5,
    "random_state":   42,
}
TEST_SIZE    = 0.2
RANDOM_STATE = 42

FEATURE_ORDER = ["area", "log_area", "bedrooms", "bathrooms", "bed_bath", "location_enc"]
TARGET_COL    = "price"

PALETTE = {}  # legacy compat shim

# ── UI palette (kept here for any legacy import) ──────────────────────────────
# Real palette lives in core/theme.py
