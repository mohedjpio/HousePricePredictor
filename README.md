# HomeVal (House Price Predictor)

HomeVal is a desktop-native application offering machine-learning-powered real estate valuations, descriptive data analytics, and embedded Large Language Model queries.

## Features
- **Machine Learning Valuations:** Get accurate predictions for house prices based on an optimized `HistGradientBoostingRegressor` model trained on a 30,000+ Egyptian property dataset. 
- **Model Details & Performance:** The Core Engine pre-caches the model for swift loading using `.pkl` serialization. 
  - Tracks metrics such as R² Score, Mean Absolute Error (MAE), RMSE, and Cross-Validation variance.
  - Automatically handles missing data and categorical encodings (condition, finishing, furnishing, views) without crashing the pipeline.
- **Descriptive Analytics:** Analyze details dynamically within the application UI.
- **Embedded LLM Queries:** Ask questions and get insights using the embedded LLM interface.
- **Modern UI:** Built using standard `tkinter` with modular widgets, supporting both dynamic theming and localization.
- **Data Persistency:** Supports funneling newly predicted instances back to a persistent local CSV dataset.

## Installation

### Prerequisites
- Python 3.8+
- Requirements listed in `requirements.txt`

### Setup Steps
1. Clone the repository and navigate to the project root:
   ```bash
   cd HousePricePredictor
   ```
2. Set up a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables (if applicable):
   - Copy `.env.example` to `.env` and provide the required API keys (e.g., `GROQ_KEY`).

## Usage

Simply run `main.py` from the project root:

```bash
python main.py
```

## Documentation
For further details, architecture design, and development guides, please check the following markdown files:
- [DEVELOPER.md](DEVELOPER.md) - Contains technical details and development setup.
- [DOCUMENTATION.md](DOCUMENTATION.md) - General architecture and system components.
- [USER_GUIDE.md](USER_GUIDE.md) - A guide for end-users interacting with HomeVal.
- [CODE_REFERENCE.md](CODE_REFERENCE.md) - Low-level reference of classes and methods.

## License
MIT (or insert equivalent depending on your release choice)
