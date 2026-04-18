"""
Reusable Tkinter widgets — fully theme-aware and RTL-capable.
Every widget accepts a `theme` kwarg and re-renders on apply_theme().
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from core.theme import Theme


class ToggleSwitch(tk.Canvas):
    W, H, R = 44, 24, 10

    def __init__(self, parent, variable: tk.IntVar, theme: Theme, **kw):
        super().__init__(parent, width=self.W, height=self.H,
                         bg=kw.pop("bg", theme.surface),
                         highlightthickness=0, cursor="hand2", **kw)
        self.var = variable
        self.theme = theme
        self._draw()
        self.bind("<Button-1>", self._toggle)
        self.var.trace_add("write", lambda *_: self._draw())

    def apply_theme(self, theme: Theme, bg=None):
        self.theme = theme
        self.configure(bg=bg or theme.surface)
        self._draw()

    def _draw(self):
        self.delete("all")
        on = bool(self.var.get())
        track = self.theme.tog_on if on else self.theme.tog_off
        cx = self.W - self.R - 5 if on else self.R + 5
        self._rrect(2, 2, self.W - 2, self.H - 2, self.H // 2 - 2,
                    fill=track, outline="")
        self.create_oval(cx - self.R, self.H // 2 - self.R,
                         cx + self.R, self.H // 2 + self.R,
                         fill=self.theme.tog_knob, outline="")

    def _rrect(self, x1, y1, x2, y2, r, **kw):
        pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r,
               x2,y2-r, x2,y2, x2-r,y2, x1+r,y2,
               x1,y2, x1,y2-r, x1,y1+r, x1,y1]
        return self.create_polygon(pts, smooth=True, **kw)

    def _toggle(self, _=None):
        self.var.set(0 if self.var.get() else 1)


class FlatEntry(tk.Entry):
    def __init__(self, parent, theme: Theme, width=14, **kw):
        super().__init__(parent,
                         font=kw.pop("font", ("Calibri", 10)),
                         bg=theme.surface2, fg=theme.text,
                         insertbackground=theme.accent,
                         relief="flat", highlightthickness=1,
                         highlightbackground=theme.border,
                         highlightcolor=theme.accent,
                         width=width, **kw)
        self.theme = theme
        self.bind("<FocusIn>",  lambda _: self.configure(highlightbackground=self.theme.accent))
        self.bind("<FocusOut>", lambda _: self.configure(highlightbackground=self.theme.border))

    def apply_theme(self, theme: Theme):
        self.theme = theme
        self.configure(bg=theme.surface2, fg=theme.text,
                       insertbackground=theme.accent,
                       highlightbackground=theme.border,
                       highlightcolor=theme.accent)


class FlatCombo(ttk.Combobox):
    _configured: set = set()

    def __init__(self, parent, values: list, theme: Theme, width=14, **kw):
        style_name = f"Flat.{theme.name}.TCombobox"
        self._configure_style(style_name, theme)
        super().__init__(parent, values=values,
                         font=kw.pop("font", ("Calibri", 10)),
                         width=width, state="readonly",
                         style=style_name, **kw)
        self._style_name = style_name
        self.theme = theme

    @classmethod
    def _configure_style(cls, name, theme):
        if name in cls._configured:
            return
        s = ttk.Style()
        try:
            s.theme_use("clam")
        except Exception:
            pass
        s.configure(name,
                    fieldbackground=theme.surface2, background=theme.surface2,
                    foreground=theme.text, selectbackground=theme.accent,
                    selectforeground=theme.accent_text, arrowcolor=theme.accent,
                    bordercolor=theme.border, lightcolor=theme.border,
                    darkcolor=theme.border, relief="flat")
        s.map(name,
              fieldbackground=[("readonly", theme.surface2)],
              selectbackground=[("readonly", theme.accent)],
              selectforeground=[("readonly", theme.accent_text)])
        cls._configured.add(name)

    def apply_theme(self, theme: Theme, values=None):
        self.theme = theme
        style_name = f"Flat.{theme.name}.TCombobox"
        self._configure_style(style_name, theme)
        self.configure(style=style_name)
        if values is not None:
            self.configure(values=values)


class Divider(tk.Frame):
    def __init__(self, parent, theme: Theme, orient="h", **kw):
        cfg = dict(bg=theme.border, height=1) if orient == "h" else dict(bg=theme.border, width=1)
        super().__init__(parent, **cfg, **kw)

    def apply_theme(self, theme: Theme):
        self.configure(bg=theme.border)


class Card(tk.Frame):
    def __init__(self, parent, theme: Theme, padx=18, pady=14, **kw):
        super().__init__(parent, bg=theme.surface,
                         highlightthickness=1, highlightbackground=theme.border,
                         padx=padx, pady=pady, **kw)
        self.theme = theme

    def apply_theme(self, theme: Theme):
        self.theme = theme
        self.configure(bg=theme.surface, highlightbackground=theme.border)


class MetricTile(tk.Frame):
    def __init__(self, parent, theme: Theme, label: str, value: str,
                 badge_bg: str, value_color: str, fonts: dict, **kw):
        super().__init__(parent, bg=badge_bg,
                         highlightthickness=1, highlightbackground=theme.border,
                         padx=12, pady=8, **kw)
        self.theme = theme
        self._badge_bg = badge_bg
        self._value_color = value_color
        self._lbl_w = tk.Label(self, text=label, font=fonts["tiny"],
                               fg=theme.text_muted, bg=badge_bg)
        self._lbl_w.pack(anchor="center")
        self._val_w = tk.Label(self, text=value, font=fonts["mono"],
                               fg=value_color, bg=badge_bg)
        self._val_w.pack(anchor="center")

    def update_label(self, text: str):
        self._lbl_w.configure(text=text)

    def update_value(self, value: str):
        self._val_w.configure(text=value)

    def apply_theme(self, theme: Theme, badge_bg: str, value_color: str):
        self.theme = theme
        self._badge_bg = badge_bg
        self._value_color = value_color
        self.configure(bg=badge_bg, highlightbackground=theme.border)
        self._lbl_w.configure(bg=badge_bg, fg=theme.text_muted)
        self._val_w.configure(bg=badge_bg, fg=value_color)


class PrimaryButton(tk.Button):
    def __init__(self, parent, theme: Theme, text="", command=None, fonts=None, **kw):
        fnt = (fonts or {}).get("subhead", ("Calibri", 10, "bold"))
        super().__init__(parent, text=text, command=command, font=fnt,
                         bg=theme.accent, fg=theme.accent_text,
                         activebackground=theme.accent_hover,
                         activeforeground=theme.accent_text,
                         relief="flat", cursor="hand2",
                         padx=20, pady=8, bd=0, **kw)
        self.theme = theme
        self._bind_hover()

    def _bind_hover(self):
        self.unbind("<Enter>")
        self.unbind("<Leave>")
        self.bind("<Enter>", lambda _: self.configure(bg=self.theme.accent_hover))
        self.bind("<Leave>", lambda _: self.configure(bg=self.theme.accent))

    def apply_theme(self, theme: Theme):
        self.theme = theme
        self.configure(bg=theme.accent, fg=theme.accent_text,
                       activebackground=theme.accent_hover,
                       activeforeground=theme.accent_text)
        self._bind_hover()


class GhostButton(tk.Button):
    def __init__(self, parent, theme: Theme, text="", command=None, fonts=None, **kw):
        fnt = (fonts or {}).get("body", ("Calibri", 10))
        super().__init__(parent, text=text, command=command, font=fnt,
                         bg=theme.surface2, fg=theme.text_muted,
                         activebackground=theme.border, activeforeground=theme.text,
                         relief="flat", cursor="hand2", padx=14, pady=8, bd=0,
                         highlightthickness=1, highlightbackground=theme.border, **kw)
        self.theme = theme

    def apply_theme(self, theme: Theme):
        self.theme = theme
        self.configure(bg=theme.surface2, fg=theme.text_muted,
                       activebackground=theme.border, activeforeground=theme.text,
                       highlightbackground=theme.border)


class IconButton(tk.Button):
    def __init__(self, parent, theme: Theme, text="", command=None, fonts=None, **kw):
        fnt = (fonts or {}).get("small", ("Calibri", 9))
        super().__init__(parent, text=text, command=command, font=fnt,
                         bg=theme.surface2, fg=theme.text_muted,
                         activebackground=theme.border, activeforeground=theme.text,
                         relief="flat", cursor="hand2", padx=10, pady=5, bd=0, **kw)
        self.theme = theme

    def apply_theme(self, theme: Theme):
        self.theme = theme
        self.configure(bg=theme.surface2, fg=theme.text_muted,
                       activebackground=theme.border, activeforeground=theme.text)
