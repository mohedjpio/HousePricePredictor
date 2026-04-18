 Developer Guide

Welcome to the **House Price Predictor** developer documentation. This guide provides instructions for setting up the local environment, project structure conventions, and guidelines for extending the application.

 Prerequisites

- Python 3.9+
- Basic knowledge of Python's `tkinter` and `pandas` libraries.
- The `assets/` folder must contain `egypt_home_pricing_30k.csv` (used for retraining the model).

 Environment Setup

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd HousePricePredictor
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
    Windows:
   .\venv\Scripts\activate
    macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Rename `.env.example` to `.env` and provide your API keys:
   ```env
   GROQ_KEY=gsk_your_groq_api_key_here
   ```

5. **Run the App:**
   ```bash
   python main.py
   ```

 Project Structure
- `main.py`: The entry point. Bootstraps the application and loads the environment.
- `ui/`: Contains all visual components, widgets, tabs, and UI styling.
- `core/`: Machine learning logic (`pipeline.py`), constants, paths, and generic thematic settings.
- `assets/`: Contains raw CSV data and cached `.pkl` model files.

 Guidelines for Extension

 Adding New Features
1. **New UI Components**: Build new reusable widgets inside `ui/widgets.py` applying the internal `THEMES` dictionary for dynamic styling. 
2. **New Model Attributes**: If adding new ML features, extend the `PredictionInput` dataclass in `core/pipeline.py`, ensure data gathering in `_gather_input` reflects those additions, and update the prediction logic inside `_save_prediction_to_csv` in `ui/app.py`.

 Debugging
You can set log levels in `main.py` using `logging.basicConfig()`. Check the console for cache failures and retrain status when the model launches.
