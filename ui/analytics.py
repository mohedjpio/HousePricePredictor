"""
Analytics dashboard page — embedded matplotlib charts in a scrollable Tkinter canvas.
"""
from __future__ import annotations
import threading
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from core.config import DATA_PATH, FEATURE_ORDER, TARGET_COL, TEST_SIZE, RANDOM_STATE
from core.theme  import Theme, get_fonts
from ui import charts as C


# ── embed helper ──────────────────────────────────────────────────────────────
def _embed(fig, parent, row, col, padx=6, pady=6, sticky="nsew"):
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    widget = canvas.get_tk_widget()
    widget.grid(row=row, column=col, padx=padx, pady=pady, sticky=sticky)
    return canvas


class AnalyticsPage(tk.Frame):

    def __init__(self, parent, pipeline, theme: Theme, lang: str = "en", **kw):
        super().__init__(parent, bg=theme.bg, **kw)
        self.theme    = theme
        self.lang     = lang
        self.fonts    = get_fonts(lang)
        self.pipeline = pipeline
        self._chart_canvases: list = []
        self._built = False

        # placeholder while loading
        self._spinner = tk.Label(self, text="⟳  Building analytics…",
                                 font=self.fonts["heading"],
                                 fg=theme.text_muted, bg=theme.bg)
        self._spinner.pack(expand=True)

    def build(self):
        """Call once pipeline is ready. Runs chart generation on a thread."""
        if self._built:
            return
        threading.Thread(target=self._build_thread, daemon=True).start()

    def _build_thread(self):
        df = pd.read_csv(DATA_PATH)
        # compute test predictions for model charts
        import numpy as np
        # Keep original columns for legacy charts
        df["log_area"]     = np.log1p(df["area"])
        df["bed_bath"]     = df["bedrooms"] * df["bathrooms"]
        df["location_enc"] = df["location"].map(
            self.pipeline.loc_mean).fillna(self.pipeline.global_mean)

        # Build exact 32 features required for model
        cond_order   = ['Needs Renovation','Fair','Good','New','Excellent']
        finish_order = ['Core & Shell','Semi Finished','Fully Finished']
        furn_order   = ['Unfurnished','Partially Furnished','Furnished']
        view_order   = ['Street','City','Garden','Pool','Sea/Lake']
        
        X = pd.DataFrame()
        X['area'] = df['area']
        X['log_area'] = df['log_area']
        X['area_sq'] = df['area']**2
        X['bedrooms'] = df['bedrooms']
        X['bathrooms'] = df['bathrooms']
        X['bed_bath'] = df['bed_bath']
        X['total_rooms'] = df['bedrooms'] + df['bathrooms']
        beds_clip = df['bedrooms'].clip(lower=1)
        X['bath_ratio'] = (df['bathrooms'] / beds_clip).clip(upper=5.0)
        X['area_per_bed'] = (df['area'] / beds_clip).clip(upper=400.0)
        X['condition_enc'] = df.get('condition', pd.Series(['Good']*len(df))).apply(lambda x: cond_order.index(x) if x in cond_order else 2)
        X['finishing_enc'] = df.get('finishing_type', pd.Series(['Fully Finished']*len(df))).apply(lambda x: finish_order.index(x) if x in finish_order else 2)
        X['furnished_enc'] = df.get('furnished', pd.Series(['Unfurnished']*len(df))).apply(lambda x: furn_order.index(x) if x in furn_order else 0)
        X['view_enc'] = df.get('view_type', pd.Series(['Street']*len(df))).apply(lambda x: view_order.index(x) if x in view_order else 0)
        X['has_pool'] = df.get('has_pool', 0)
        X['has_gym'] = df.get('has_gym', 0)
        X['has_security'] = df.get('has_security', 1)
        X['has_elevator'] = df.get('has_elevator', 1)
        X['has_balcony'] = df.get('has_balcony', 1)
        X['is_compound'] = df.get('is_compound', 0)
        X['amenity_score'] = df.get('amenity_score', X['has_pool'] + X['has_gym'] + X['has_security'] + X['has_elevator'] + X['has_balcony'] + X['is_compound'])
        X['parking_spaces'] = df.get('parking_spaces', 1)
        X['garden_sqm'] = df.get('garden_sqm', 0)
        X['floor_number'] = df.get('floor_number', 3)
        X['building_age_years'] = df.get('building_age_years', 5)
        X['age_sq'] = X['building_age_years']**2
        X['new_building'] = (X['building_age_years'] <= 2).astype(int)
        X['floor_to_ceiling_height_m'] = df.get('floor_to_ceiling_height_m', 3.0)
        X['distance_to_center_km'] = df.get('distance_to_center_km', 10.0)
        X['distance_to_metro_km'] = df.get('distance_to_metro_km', 2.0)
        X['luxury_flag'] = df.get('luxury_flag', (X['bath_ratio'] > 1).astype(int))
        X['location_enc'] = df['location_enc']
        X['title_enc'] = self.pipeline.global_title

        features = self.pipeline._payload['features']
        X = X[features]
        y = df[TARGET_COL]
        _, X_test, _, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE)
        
        y_pred = self.pipeline.model.predict(X_test)

        feat_labels = [f.replace('_', ' ').title() for f in features]
        T = self.theme

        figs = {
            "kpi":        C.kpi_strip(df, T),
            "price_dist": C.price_distribution(df, T),
            "top_loc":    C.top_locations(df, T),
            "scatter":    C.area_vs_price(df, T),
            "donut":      C.property_type_donut(df, T),
            "beds":       C.bedrooms_dist(df, T),
            "ppm":        C.ppm_by_location(df, T),
            "avp":        C.actual_vs_predicted(y_test, y_pred, T),
            "feat_imp":   C.feature_importance(self.pipeline.model, X_test, y_test, feat_labels, T),
            "resid":      C.residuals_hist(y_test, y_pred, T),
        }
        self.after(0, lambda: self._render(figs, df))

    def _render(self, figs, df):
        self._spinner.destroy()
        T = self.theme; F = self.fonts

        # scrollable canvas
        outer = tk.Frame(self, bg=T.bg)
        outer.pack(fill="both", expand=True)
        vbar = tk.Scrollbar(outer, orient="vertical")
        hbar = tk.Scrollbar(outer, orient="horizontal")
        vbar.pack(side="right", fill="y")
        hbar.pack(side="bottom", fill="x")
        canvas = tk.Canvas(outer, bg=T.bg, highlightthickness=0,
                           yscrollcommand=vbar.set, xscrollcommand=hbar.set)
        canvas.pack(fill="both", expand=True)
        vbar.config(command=canvas.yview)
        hbar.config(command=canvas.xview)

        inner = tk.Frame(canvas, bg=T.bg)
        cwin  = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_cfg(e): canvas.configure(scrollregion=canvas.bbox("all"))
        def _on_resize(e): canvas.itemconfig(cwin, width=e.width)
        inner.bind("<Configure>", _on_cfg)
        canvas.bind("<Configure>", _on_resize)
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        canvas.bind("<Button-4>",   lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind("<Button-5>",   lambda e: canvas.yview_scroll( 1, "units"))

        pad = dict(padx=8, pady=8)

        # ── Section: KPI strip ────────────────────────────────────────────────
        self._section_label(inner, "📊  Market Overview", T, F).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(16,4))
        kpi_cv = FigureCanvasTkAgg(figs["kpi"], master=inner)
        kpi_cv.draw()
        kpi_cv.get_tk_widget().grid(row=1, column=0, columnspan=2,
                                    sticky="ew", padx=8, pady=(0,8))
        self._chart_canvases.append(kpi_cv)

        # ── Section: Data Analysis ────────────────────────────────────────────
        self._section_label(inner, "📈  Data Analysis", T, F).grid(
            row=2, column=0, columnspan=2, sticky="w", padx=12, pady=(8,4))

        for i, (key, r, c) in enumerate([
            ("price_dist", 3, 0), ("top_loc",  3, 1),
            ("scatter",    4, 0), ("ppm",       4, 1),
            ("donut",      5, 0), ("beds",      5, 1),
        ]):
            cv = FigureCanvasTkAgg(figs[key], master=inner)
            cv.draw()
            cv.get_tk_widget().grid(row=r, column=c, sticky="nsew", **pad)
            self._chart_canvases.append(cv)

        # ── Section: Model Performance ────────────────────────────────────────
        self._section_label(inner, "🤖  Model Performance", T, F).grid(
            row=6, column=0, columnspan=2, sticky="w", padx=12, pady=(8,4))

        # Model metrics tiles
        metrics_frame = tk.Frame(inner, bg=T.bg)
        metrics_frame.grid(row=7, column=0, columnspan=2, sticky="ew", padx=8, pady=(0,8))
        m = self.pipeline.metrics
        kpis = [
            ("R² Score",        f"{m.r2:.4f}",       T.accent),
            ("MAE",             f"E£{m.mae/1e6:.2f}M", T.success),
            ("RMSE",            f"E£{m.rmse/1e6:.2f}M", T.warning),
            ("CV R² (5-fold)",  f"{m.cv_r2_mean:.4f} ± {m.cv_r2_std:.3f}", T.text_muted),
            ("Train Samples",   f"{m.n_train:,}",     T.accent),
            ("Test Samples",    f"{m.n_test:,}",      T.success),
        ]
        for i, (lbl, val, color) in enumerate(kpis):
            tile = tk.Frame(metrics_frame, bg=T.surface,
                            highlightthickness=1, highlightbackground=T.border)
            tile.grid(row=0, column=i, padx=(0 if i==0 else 6, 0), sticky="ew")
            metrics_frame.columnconfigure(i, weight=1)
            tk.Label(tile, text=val,  font=F["mono_lg"], fg=color,
                     bg=T.surface, pady=4).pack()
            tk.Label(tile, text=lbl,  font=F["tiny"],  fg=T.text_muted,
                     bg=T.surface).pack(pady=(0,6))

        for key, r, c in [("avp", 8, 0), ("feat_imp", 8, 1),
                           ("resid", 9, 0)]:
            cv = FigureCanvasTkAgg(figs[key], master=inner)
            cv.draw()
            cv.get_tk_widget().grid(row=r, column=c, sticky="nsew", **pad)
            self._chart_canvases.append(cv)

        # configure grid weights
        inner.columnconfigure(0, weight=1)
        inner.columnconfigure(1, weight=1)

        self._built = True
        self._inner = inner

    def _section_label(self, parent, text, theme, fonts):
        lbl = tk.Label(parent, text=text, font=fonts["heading"],
                       fg=theme.text, bg=theme.bg)
        return lbl

    def apply_theme(self, theme: Theme):
        """Rebuild charts on theme change."""
        self.theme = theme
        if self._built:
            self._built = False
            for w in self.winfo_children():
                w.destroy()
            self._chart_canvases.clear()
            self._spinner = tk.Label(self, text="⟳  Rebuilding charts…",
                                     font=self.fonts["heading"],
                                     fg=theme.text_muted, bg=theme.bg)
            self._spinner.pack(expand=True)
            self.build()
