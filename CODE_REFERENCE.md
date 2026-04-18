# Project Function Directory & Code Reference

This document maps out and explains the purpose of the primary functions utilized across the codebase.

## 1. Entry Point (`main.py`)
No explicit functions, but houses the procedural bootstrap resolving Python's `sys.path` dynamically, loading `.env` file credentials securely via `dotenv`, and injecting dependencies required for the UI to spawn via `HousePriceApp().mainloop()`.

---

## 2. UI Subsystem (`ui/app.py`)
This file contains the `HousePriceApp` class encompassing the primary operational behaviors for the desktop app.

- `__init__(self)`: Instantiates the TKinter loop window, default screen dimensions, configures local dictionaries, and triggers downstream background tasks (like `_load_model_async`).
- `_build_ui(self)`: Main skeleton generator. Draws headers, the bottom status bar, and acts as a router mapping three distinct frame pages.
- `_build_estimator(self, parent)` / `_build_form_scroll(self, parent)` / `_build_form_content(self, parent)`: Cascading setup of the Estimator View, managing scrollbars and inserting form `FlatEntry` fields into visual Cards for data like dimensions, quality, amenities, and location.
- `_build_chat_page(self, parent)`: Bootstraps the visual canvas and header containing the AI Groq API Assistant layout.
- `_add_chat_bubble(self, role, text)`: Helper method generating individual message UI elements attached dynamically to the chat canvas.
- `_save_key(self)`: Performs basic validation mapping a UI-inputted token to memory for Groq usage.
- `_on_chat_send(self)`: Formatter dispatching current text-box values out to a background API caller.
- `_groq_call(self)`: Synchronous blocking API call resolving HTTP REST definitions to the external `https://api.groq.com/openai/v1/chat/completions` endpoint, then updating UI threads with the Model's reply.
- `_switch_tab(self, tab_id)`: A routing utility promoting particular page frames to the top-most level array rendering it visible to the user.
- `_build_analytics_widget(self)`: Lazily builds out the Analytics visuals on memory hit when the user requests the analytics view for the first time.
- `_load_model_async(self)` & `_on_model_ready(self)`: Parallel thread managers invoking `HousingPipeline()`. Notifies UI status on completions preventing window lockup during large model parsing.
- `_filter_locations(self, *_)` / `_refresh_listbox(self, locs)`: Triggers and search-index methods sorting via the Egyptian location dataset array logic for dropdowns.
- `_gather_input(self)`: Utility packaging individual TKinter string variables into a strongly-typed `PredictionInput` dataclass.
- `_on_predict(self)`: Primary invocation handler firing inputs towards the pipeline and refreshing prediction results onto the application Canvas. Calls CSV persistence.
- `_save_prediction_to_csv(self, inp, result)`: A parallel worker managing File I/O encoding inputs/outputs continuously into `assets/egypt_home_pricing_30k.csv`.
- `_on_reset(self)`: Empties application cache, removing predictions from screen.
- `_on_retrain(self)`: Starts a UI-level signal asking `core` to rebuild the cached model on current known CSV bounds.
- `_toggle_theme(self)` / `_apply_theme_colors(self)`: Cycles visual logic maps (dark vs light mode parameters) over recursive widget loops overriding backgrounds and font colors dynamically.
- `_toggle_lang(self)` / `_rebuild_text(self)`: Handles English to Arabic translations via pointer matching `theme.py` data maps.
- `_draw_bar(self)`: Creates a visual rectangle gradient logic mapping the confidence bounds.

---

## 3. Core Engine (`core/pipeline.py`)
This file controls intelligence features independent of user interface layers.

- `PredictionInput.to_dataframe(self, payload)`: Unpacks isolated `dataclass` parameters mapping them to Scikit-Learn normalized distributions resulting in a single-row `pd.DataFrame`.
- `HousingPipeline.__init__(self)`: Constructor loading dataset statistics boundaries caching them immediately via `_load_or_train()`.
- `HousingPipeline.predict(self, inp)`: Main machine learning executor converting user classes to a float price resulting in an encapsulated `PredictionResult`.
- `HousingPipeline.retrain(self)`: Destructively clears `.pkl` files and forces an entirely fresh DataFrame evaluation on `.csv` bounds.
- `HousingPipeline._load_or_train(self)` & `HousingPipeline._load_cached(self)`: Fallback handling checking the local disk path resolving binary ML caches if possible to omit heavy runtime setups.
- `HousingPipeline._train_and_cache(self)`: Directly interfaces via Pandas resolving `egypt_housing_engineered.csv` building out an updated Histogram Gradient Boosting model structure.
