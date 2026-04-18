# HomeVal — House Price Estimator

AI-powered desktop application that predicts house prices using a Gradient Boosting Regressor trained on real housing data.

## Project Structure

```
HousePricePredictor/
├── main.py               # Entry point
├── requirements.txt
├── assets/
│   └── Housing.csv       # Training dataset (545 rows, 13 features)
├── models/
│   └── housing_model.pkl # Cached trained model (auto-generated)
├── core/
│   ├── config.py         # Paths, constants, palette, fonts
│   └── pipeline.py       # Data loading, training, prediction
└── ui/
    ├── widgets.py         # Reusable styled Tkinter components
    └── app.py             # Main window (View + Controller)
```

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

The model trains automatically on first launch and is cached to `models/housing_model.pkl` for fast subsequent startups.

## Model Performance

| Metric        | Value         |
|---------------|---------------|
| R² Score      | ~0.990      |
| MAE           | ~₹10.1 Lakh   |
| Algorithm     | Gradient Boosting Regressor |
| Dataset       | 545 samples   |

## Features

- 12 input features: area, bedrooms, bathrooms, stories, parking, furnishing, and 6 binary amenity flags
- Async model loading — UI is never blocked
- Confidence range display (±12% of predicted price)
- Clean MVC-style architecture
- Fully dark, GitHub-inspired UI
