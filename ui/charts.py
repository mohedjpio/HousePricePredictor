"""
Charts module — all matplotlib figures for the Analytics dashboard.
Each function returns a matplotlib Figure ready to embed in Tkinter.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from core.theme import Theme

# ── palette helpers ───────────────────────────────────────────────────────────
def _hex(h: str) -> str:
    return f"#{h}" if not h.startswith("#") else h

def _fig(theme: Theme, w: float, h: float) -> Figure:
    fig = Figure(figsize=(w, h), facecolor=theme.surface)
    return fig

def _style_ax(ax, theme: Theme, grid: bool = True):
    ax.set_facecolor(theme.surface2)
    ax.tick_params(colors=theme.text_muted, labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(theme.border)
    if grid:
        ax.grid(axis="y", color=theme.border, linewidth=0.6, linestyle="--", alpha=0.7)
        ax.set_axisbelow(True)
    ax.title.set_color(theme.text)
    ax.title.set_fontsize(10)
    ax.title.set_fontweight("bold")
    if ax.get_xlabel():
        ax.xaxis.label.set_color(theme.text_muted)
        ax.xaxis.label.set_fontsize(8)
    if ax.get_ylabel():
        ax.yaxis.label.set_color(theme.text_muted)
        ax.yaxis.label.set_fontsize(8)


# ── 1. KPI strip (4 stat cards as a figure) ──────────────────────────────────
def kpi_strip(df: pd.DataFrame, theme: Theme) -> Figure:
    fig = Figure(figsize=(10, 1.4), facecolor=theme.bg)
    kpis = [
        ("Total Listings",       f"{len(df):,}",                theme.accent),
        ("Avg. Price",           f"E£{df.price.mean()/1e6:.2f}M", theme.success),
        ("Avg. Area",            f"{df.area.mean():.0f} m²",     theme.warning),
        ("Avg. Price/m²",        f"E£{df.price_per_meter.mean():,.0f}", theme.text_muted),
    ]
    for i, (label, value, color) in enumerate(kpis):
        ax = fig.add_axes([i * 0.25 + 0.01, 0.05, 0.23, 0.90])
        ax.set_facecolor(theme.surface)
        for sp in ax.spines.values():
            sp.set_edgecolor(color)
            sp.set_linewidth(1.5)
        ax.set_xticks([]); ax.set_yticks([])
        ax.text(0.5, 0.62, value, transform=ax.transAxes,
                ha="center", va="center", fontsize=15, fontweight="bold",
                color=color, fontfamily="monospace")
        ax.text(0.5, 0.18, label, transform=ax.transAxes,
                ha="center", va="center", fontsize=8,
                color=theme.text_muted)
    return fig


# ── 2. Price distribution histogram ──────────────────────────────────────────
def price_distribution(df: pd.DataFrame, theme: Theme) -> Figure:
    fig = _fig(theme, 5, 3.2)
    ax = fig.add_subplot(111)
    prices = df["price"] / 1e6
    n, bins, patches = ax.hist(prices, bins=40, color=theme.accent,
                                edgecolor=theme.surface, linewidth=0.4, alpha=0.85)
    # gradient colour by value
    norm = plt.Normalize(bins.min(), bins.max())
    cmap = matplotlib.colormaps.get_cmap("Blues")
    for patch, left in zip(patches, bins[:-1]):
        patch.set_facecolor(cmap(norm(left) * 0.7 + 0.3))
    ax.axvline(prices.median(), color=theme.success, lw=1.5, linestyle="--", label=f"Median E£{prices.median():.1f}M")
    ax.axvline(prices.mean(),   color=theme.warning,  lw=1.5, linestyle=":",  label=f"Mean E£{prices.mean():.1f}M")
    ax.set_title("Price Distribution")
    ax.set_xlabel("Price (E£ Millions)")
    ax.set_ylabel("Count")
    ax.legend(fontsize=7, facecolor=theme.surface, edgecolor=theme.border,
              labelcolor=theme.text_muted)
    _style_ax(ax, theme)
    fig.tight_layout(pad=1.2)
    return fig


# ── 3. Top 12 locations by avg price ─────────────────────────────────────────
def top_locations(df: pd.DataFrame, theme: Theme) -> Figure:
    fig = _fig(theme, 5, 3.2)
    ax = fig.add_subplot(111)
    top = (df[df.location != "Unknown"]
           .groupby("location")["price"]
           .median()
           .sort_values(ascending=False)
           .head(12))
    colors = [theme.accent if i < 3 else theme.surface2
              for i in range(len(top))]
    bars = ax.barh(top.index[::-1], top.values[::-1] / 1e6,
                   color=colors[::-1], edgecolor=theme.border, linewidth=0.5, height=0.65)
    for bar, val in zip(bars, top.values[::-1] / 1e6):
        ax.text(val + 0.05, bar.get_y() + bar.get_height() / 2,
                f"E£{val:.1f}M", va="center", fontsize=7, color=theme.text_muted)
    ax.set_title("Median Price by Location (Top 12)")
    ax.set_xlabel("Median Price (E£ Millions)")
    ax.tick_params(axis="y", labelsize=7)
    _style_ax(ax, theme, grid=False)
    ax.grid(axis="x", color=theme.border, linewidth=0.6, linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)
    fig.tight_layout(pad=1.2)
    return fig


# ── 4. Area vs Price scatter ──────────────────────────────────────────────────
def area_vs_price(df: pd.DataFrame, theme: Theme) -> Figure:
    fig = _fig(theme, 5, 3.2)
    ax = fig.add_subplot(111)
    sample = df.sample(min(2000, len(df)), random_state=42)
    sc = ax.scatter(sample["area"], sample["price"] / 1e6,
                    c=sample["bedrooms"], cmap="Blues",
                    alpha=0.45, s=12, edgecolors="none")
    # trend line
    z = np.polyfit(sample["area"], sample["price"] / 1e6, 1)
    xs = np.linspace(sample["area"].min(), sample["area"].max(), 200)
    ax.plot(xs, np.poly1d(z)(xs), color=theme.accent, lw=1.5, alpha=0.8)
    cbar = fig.colorbar(sc, ax=ax, pad=0.02)
    cbar.ax.tick_params(colors=theme.text_muted, labelsize=7)
    cbar.set_label("Bedrooms", color=theme.text_muted, fontsize=7)
    ax.set_title("Area vs Price (coloured by bedrooms)")
    ax.set_xlabel("Area (m²)")
    ax.set_ylabel("Price (E£ Millions)")
    _style_ax(ax, theme)
    fig.tight_layout(pad=1.2)
    return fig


# ── 5. Property type pie / donut ──────────────────────────────────────────────
def property_type_donut(df: pd.DataFrame, theme: Theme) -> Figure:
    fig = _fig(theme, 4, 3.2)
    ax = fig.add_subplot(111)
    counts = df["title"].value_counts()
    palette = [theme.accent, theme.success, theme.warning, theme.error,
               theme.text_muted, theme.accent_hover]
    wedges, texts, autotexts = ax.pie(
        counts.values, labels=counts.index,
        autopct="%1.1f%%", startangle=90,
        colors=palette[:len(counts)],
        wedgeprops=dict(width=0.55, edgecolor=theme.surface, linewidth=2),
        textprops=dict(color=theme.text, fontsize=8),
    )
    for at in autotexts:
        at.set_fontsize(7.5)
        at.set_color(theme.surface)
        at.set_fontweight("bold")
    ax.set_title("Property Type Mix")
    _style_ax(ax, theme, grid=False)
    fig.tight_layout(pad=1.2)
    return fig


# ── 6. Bedrooms distribution bar ─────────────────────────────────────────────
def bedrooms_dist(df: pd.DataFrame, theme: Theme) -> Figure:
    fig = _fig(theme, 4, 3.2)
    ax = fig.add_subplot(111)
    counts = df["bedrooms"].value_counts().sort_index()
    bars = ax.bar(counts.index.astype(str), counts.values,
                  color=theme.accent, edgecolor=theme.surface,
                  linewidth=0.5, width=0.6)
    bars[counts.values.argmax()].set_color(theme.success)
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 20,
                f"{bar.get_height():,}", ha="center", va="bottom",
                fontsize=7, color=theme.text_muted)
    ax.set_title("Bedrooms Distribution")
    ax.set_xlabel("Number of Bedrooms")
    ax.set_ylabel("Listings")
    _style_ax(ax, theme)
    fig.tight_layout(pad=1.2)
    return fig


# ── 7. Price per m² by location (box-like via violin) ───────────────────────
def ppm_by_location(df: pd.DataFrame, theme: Theme) -> Figure:
    fig = _fig(theme, 5, 3.2)
    ax = fig.add_subplot(111)
    top_locs = (df[df.location != "Unknown"]
                .groupby("location")["price_per_meter"]
                .median()
                .sort_values(ascending=False)
                .head(8).index.tolist())
    sub = df[df.location.isin(top_locs)]
    data = [sub[sub.location == l]["price_per_meter"].values / 1000
            for l in top_locs]
    bp = ax.boxplot(data, vert=True, patch_artist=True,
                    medianprops=dict(color=theme.success, linewidth=2),
                    whiskerprops=dict(color=theme.border),
                    capprops=dict(color=theme.border),
                    flierprops=dict(marker="o", markersize=2,
                                    color=theme.text_dim, alpha=0.4))
    palette = [theme.accent, theme.accent_hover, theme.success,
               theme.warning, theme.error, theme.text_muted,
               theme.badge_r2, theme.badge_mae]
    for patch, color in zip(bp["boxes"], palette):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
        patch.set_edgecolor(theme.border)
    ax.set_xticks(range(1, len(top_locs) + 1))
    ax.set_xticklabels([l.replace(" ", "\n") for l in top_locs], fontsize=6.5)
    ax.set_title("Price/m² Distribution — Top 8 Locations")
    ax.set_ylabel("Price/m² (E£ thousands)")
    _style_ax(ax, theme)
    fig.tight_layout(pad=1.2)
    return fig


# ── 8. Model: Actual vs Predicted scatter ────────────────────────────────────
def actual_vs_predicted(y_test, y_pred, theme: Theme) -> Figure:
    fig = _fig(theme, 5, 3.2)
    ax = fig.add_subplot(111)
    y_t = np.array(y_test) / 1e6
    y_p = np.array(y_pred) / 1e6
    ax.scatter(y_t, y_p, alpha=0.3, s=10, color=theme.accent, edgecolors="none")
    lims = [min(y_t.min(), y_p.min()) * 0.95,
            max(y_t.max(), y_p.max()) * 1.05]
    ax.plot(lims, lims, color=theme.success, lw=1.5, linestyle="--", label="Perfect fit")
    ax.set_xlim(lims); ax.set_ylim(lims)
    ax.set_title("Actual vs Predicted Prices")
    ax.set_xlabel("Actual (E£ Millions)")
    ax.set_ylabel("Predicted (E£ Millions)")
    ax.legend(fontsize=7, facecolor=theme.surface, edgecolor=theme.border,
              labelcolor=theme.text_muted)
    _style_ax(ax, theme)
    fig.tight_layout(pad=1.2)
    return fig


# ── 9. Feature importance bar ─────────────────────────────────────────────────
def feature_importance(model, X_test, y_test, feature_names: list, theme: Theme) -> Figure:
    fig = _fig(theme, 4, 3.2)
    ax = fig.add_subplot(111)
    
    if hasattr(model, 'feature_importances_'):
        imp = model.feature_importances_
    else:
        from sklearn.inspection import permutation_importance
        # Compute fast permutation importance for models like HistGBR
        result = permutation_importance(model, X_test.sample(min(2000, len(X_test)), random_state=42),
                                        y_test.loc[X_test.sample(min(2000, len(X_test)), random_state=42).index],
                                        n_repeats=1, random_state=42)
        imp = result.importances_mean
        
    order = np.argsort(imp)[-10:] # Top 10 to avoid crowding the chart
    labels = [feature_names[i] for i in order]
    values = imp[order]
    colors = [theme.success if v == values.max() else theme.accent for v in values]
    ax.barh(labels, values, color=colors, edgecolor=theme.surface,
            linewidth=0.5, height=0.6)
    for i, v in enumerate(values):
        ax.text(v + 0.002, i, f"{v:.3f}", va="center",
                fontsize=7.5, color=theme.text_muted)
    ax.set_title("Feature Importance")
    ax.set_xlabel("Importance Score")
    _style_ax(ax, theme, grid=False)
    ax.grid(axis="x", color=theme.border, linewidth=0.6, linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)
    fig.tight_layout(pad=1.2)
    return fig


# ── 10. Residuals histogram ───────────────────────────────────────────────────
def residuals_hist(y_test, y_pred, theme: Theme) -> Figure:
    fig = _fig(theme, 5, 3.2)
    ax = fig.add_subplot(111)
    resid = (np.array(y_pred) - np.array(y_test)) / 1e6
    ax.hist(resid, bins=40, color=theme.accent, edgecolor=theme.surface,
            linewidth=0.3, alpha=0.85)
    ax.axvline(0, color=theme.success, lw=2, linestyle="--", label="Zero error")
    ax.axvline(resid.mean(), color=theme.warning, lw=1.5,
               linestyle=":", label=f"Mean {resid.mean():.2f}M")
    ax.set_title("Residuals Distribution")
    ax.set_xlabel("Predicted − Actual (E£ Millions)")
    ax.set_ylabel("Count")
    ax.legend(fontsize=7, facecolor=theme.surface, edgecolor=theme.border,
              labelcolor=theme.text_muted)
    _style_ax(ax, theme)
    fig.tight_layout(pad=1.2)
    return fig
