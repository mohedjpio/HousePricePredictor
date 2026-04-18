# General Documentation (Architecture & Concepts)

## Application Overview
HomeVal (House Price Predictor) is a desktop-native application offering machine-learning-powered real estate valuations, descriptive data analytics, and embedded Large Language Model queries.

## Architecture

The project maintains a strict separation of concerns, divided generally into the **UI Subsystem** and the **Core Engine**.

### UI Subsystem (`ui/`)
Built with standard `tkinter`, the UI uses an object-oriented approach leveraging modular widgets mapping closely to Modern UI semantics (Cards, Divider, Ghost/Primary Buttons, etc.).
- The UI handles the `Theme` and `Lang` paradigms via dynamic re-renders on dictionaries imported from `core.theme`.
- The `HousePriceApp` holds all tabs in memory and toggles their layer sequence utilizing `.lift()` instead of aggressively destroying/rebuilding them.

### Core Engine (`core/`)
Machine Learning operations are safely encapsulated here. 
- The **ML Pipeline** reads Egyptian housing data (30,000+ entries) parsing them via `HistGradientBoostingRegressor` from `scikit-learn`.
- Instead of retraining per boot, `core/pipeline.py` maintains an optimized `.pkl` cache. A background thread runs model instantiation off the UI thread avoiding blocking interactions.
- User input payloads are strictly mapped using dataclasses to avoid type errors causing crashes in native environments.

### Data Persistency
Data from newly predicted instances are funneled through `ui/app.py` directly into a persistent flat-file CSV appended to `assets/egypt_home_pricing_30k.csv`. These records then become available to the user upon hitting "Retrain".

### Secrets Management
API keys (such as `GROQ_KEY`) are removed from version control. `python-dotenv` loads instances securely from the local `.env` definition exclusively at runtime via `main.py`.
