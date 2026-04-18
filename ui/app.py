"""
HomeVal — Main application window.
Tabs: Estimator | Analytics | AI Chat
Fully resizable / maximizable, dark+light, AR/EN.
"""
from __future__ import annotations
import os, threading, tkinter as tk
from tkinter import messagebox, ttk

from core.pipeline  import HousingPipeline, PredictionInput
from core.theme     import THEMES, STRINGS, get_fonts, Theme
from ui.widgets     import (Card, Divider, FlatEntry, FlatCombo,
                             PrimaryButton, GhostButton, IconButton, MetricTile)
from ui.analytics   import AnalyticsPage

# ── AI Chat imports ───────────────────────────────────────────────
import urllib.request, urllib.error, json as _json

GROQ_MODEL = "llama-3.1-8b-instant"
GROQ_KEY   = os.environ.get("GROQ_KEY", "")   # set via app Settings or env var

CHAT_SYSTEM = """You are HomeVal AI — an expert real estate assistant specializing in the Egyptian 
property market. You help users understand property prices, neighborhoods, investment advice, 
buying/selling tips, and market trends in Egypt. Be concise, helpful, and always respond in 
the same language the user writes in (Arabic or English). When giving price estimates, 
mention that accurate estimates can be obtained from the HomeVal estimator tool."""


class HousePriceApp(tk.Tk):
    MIN_W, MIN_H = 1050, 680

    def __init__(self):
        super().__init__()
        self.title("HomeVal  ·  Property Valuation")
        self.minsize(self.MIN_W, self.MIN_H)
        self.geometry(f"{self.MIN_W}x{self.MIN_H}")
        try:    self.state("zoomed")
        except: self.attributes("-zoomed", True)

        self._lang   = "en"; self._theme = THEMES["dark"]; self._fonts = get_fonts("en")
        self._pipeline = None; self._loading = True; self._active_tab = "estimator"

        self._input_vars:dict={}; self._toggle_vars:dict={}
        self._combo_refs:list=[]; self._entry_refs:list=[]; self._metric_tiles:dict={}
        self._price_var = tk.StringVar(value="—"); self._range_var = tk.StringVar(value="")
        self._bar_pct = 0.0; self._analytics_widget = None
        self._chat_history:list = []  # list of (role, text)
        self._groq_key = tk.StringVar(value=GROQ_KEY)

        self._load_icons()
        self._build_ui()
        self._apply_theme_colors()
        self._center()
        self._load_model_async()

    def _load_icons(self):
        from pathlib import Path
        try:
            from PIL import Image, ImageTk
        except ImportError:
            Image = ImageTk = None

        self._icons = {}
        icons_dir = Path(__file__).resolve().parent.parent / "assets" / "icons"
        icons_dir.mkdir(parents=True, exist_ok=True)
        names = ["estimator", "analytics", "chat", "theme_light", "theme_dark", "search", "retrain", "bot", "user", "send"]
        
        # Desired UI resolutions for each icon type
        icon_sizes = {
            "estimator": 24, "analytics": 24, "chat": 24,
            "theme_light": 20, "theme_dark": 20, "search": 16,
            "retrain": 20, "bot": 32, "user": 32, "send": 20
        }

        for nm in names:
            p = icons_dir / f"{nm}.png"
            if p.exists():
                try:
                    if Image is not None and ImageTk is not None:
                        img = Image.open(str(p)).convert("RGBA")
                        size = icon_sizes.get(nm, 24)
                        # high-quality downsampling if PIL is available
                        img = img.resize((size, size), Image.Resampling.LANCZOS)
                        self._icons[nm] = ImageTk.PhotoImage(img)
                    else:
                        base_img = tk.PhotoImage(file=str(p))
                        size = icon_sizes.get(nm, 24)
                        # native fallback assumes 256x256 input
                        scale_factor = max(1, 256 // size)
                        self._icons[nm] = base_img.subsample(scale_factor, scale_factor)
                except Exception as e:
                    print(f"Error loading icon {nm}: {e}")
                    self._icons[nm] = None
            else:
                self._icons[nm] = None

        app_icon_path = icons_dir / "HousePricePredictor.png"
        if app_icon_path.exists():
            try:
                if Image is not None and ImageTk is not None:
                    app_img = ImageTk.PhotoImage(Image.open(str(app_icon_path)).convert("RGBA"))
                else:
                    app_img = tk.PhotoImage(file=str(app_icon_path))
                self.iconphoto(True, app_img)
                self._app_icon = app_img
            except Exception as e:
                print(f"Error loading app icon: {e}")

    # ── UI skeleton ───────────────────────────────────────────────
    def _build_ui(self):
        T=self._theme; F=self._fonts
        # top bar
        self._topbar = tk.Frame(self,bg=T.header_bg,height=52,
                                highlightthickness=1,highlightbackground=T.header_bdr)
        self._topbar.pack(fill="x",side="top"); self._topbar.pack_propagate(False)
        logo=tk.Frame(self._topbar,bg=T.header_bg); logo.pack(side="left",padx=(20,0))
        self._dot=tk.Canvas(logo,width=10,height=10,bg=T.header_bg,highlightthickness=0)
        self._dot.create_oval(0,0,10,10,fill=T.accent,outline="",tags="dot"); self._dot.pack(side="left",pady=16,padx=(0,8))
        self._app_name_lbl=tk.Label(logo,text=self._s("app_name"),font=F["display"],fg=T.text,bg=T.header_bg); self._app_name_lbl.pack(side="left")
        tabs=tk.Frame(self._topbar,bg=T.header_bg); tabs.pack(side="left",padx=28)
        self._tab_btns={}
        for tid,icon,lk in [("estimator","🏠","tab_estimator"),("analytics","📊","tab_analytics"),("chat","💬","tab_chat")]:
            img = self._icons.get(tid)
            txt = f" {self._s(lk)} " if img else f"  {icon}  {self._s(lk)}  "
            btn=tk.Button(tabs,text=txt,font=F["body"],
                          image=img if img else "", compound="left" if img else "none",
                          bg=T.header_bg,fg=T.text,activebackground=T.surface2,activeforeground=T.accent,
                          relief="flat",cursor="hand2",bd=0,pady=14,
                          command=lambda t=tid:self._switch_tab(t))
            btn.pack(side="left",padx=2); self._tab_btns[tid]=btn
        toolbar=tk.Frame(self._topbar,bg=T.header_bg,padx=16); toolbar.pack(side="right")
        self._lang_btn=IconButton(toolbar,T,text=self._s("lang_toggle"),command=self._toggle_lang,fonts=F); self._lang_btn.pack(side="right",padx=(4,0))
        is_dark = T.name=="dark"
        img = self._icons.get("theme_light" if is_dark else "theme_dark")
        txt = self._s("theme_light" if is_dark else "theme_dark") if img else ("☀  " if is_dark else "☾  ") + self._s("theme_light" if is_dark else "theme_dark")
        self._theme_btn=IconButton(toolbar,T,text=txt, image=img if img else "", compound="left" if img else "none", command=self._toggle_theme,fonts=F); self._theme_btn.pack(side="right",padx=(4,0))
        Divider(toolbar,T,orient="v").pack(side="right",fill="y",padx=(8,4),pady=10)
        self._toolbar_dividers=[toolbar.winfo_children()[-1]]
        # status bar
        self._statusbar=tk.Frame(self,bg=T.surface2,height=24,highlightthickness=1,highlightbackground=T.border); self._statusbar.pack(fill="x",side="bottom"); self._statusbar.pack_propagate(False)
        self._status_var=tk.StringVar(value=self._s("loading"))
        self._status_lbl=tk.Label(self._statusbar,textvariable=self._status_var,font=F["tiny"],fg=T.text_dim,bg=T.surface2,anchor="w"); self._status_lbl.pack(side="left",padx=12)
        self._subtitle_lbl=tk.Label(self._statusbar,text=self._s("app_subtitle"),font=F["tiny"],fg=T.text_dim,bg=T.surface2,anchor="e"); self._subtitle_lbl.pack(side="right",padx=12)
        # pages
        self._pages=tk.Frame(self,bg=T.bg); self._pages.pack(fill="both",expand=True)
        self._estimator_page=tk.Frame(self._pages,bg=T.bg)
        self._analytics_page_holder=tk.Frame(self._pages,bg=T.bg)
        self._chat_page=tk.Frame(self._pages,bg=T.bg)
        for p in [self._estimator_page,self._analytics_page_holder,self._chat_page]:
            p.place(relx=0,rely=0,relwidth=1,relheight=1)
        self._build_estimator(self._estimator_page)
        self._build_chat_page(self._chat_page)
        self._switch_tab("estimator")

    # ── Estimator ─────────────────────────────────────────────────
    def _build_estimator(self,parent):
        T=self._theme; F=self._fonts
        # sidebar
        self._sidebar=tk.Frame(parent,bg=T.sidebar_bg,width=300); self._sidebar.pack(side="left",fill="y"); self._sidebar.pack_propagate(False)
        inner=tk.Frame(self._sidebar,bg=T.sidebar_bg,padx=20,pady=20); inner.pack(fill="both",expand=True)
        self._metrics_title=tk.Label(inner,text=self._s("model_metrics"),font=F["subhead"],fg=T.text_muted,bg=T.sidebar_bg); self._metrics_title.pack(anchor="w",pady=(0,10))
        self._loading_lbl=tk.Label(inner,text=self._s("loading"),font=F["small"],fg=T.text_dim,bg=T.sidebar_bg); self._loading_lbl.pack(anchor="w")
        self._metrics_grid=tk.Frame(inner,bg=T.sidebar_bg)
        for i,(key,lk,bg,col) in enumerate([("r2","r2_label",T.badge_r2,T.accent),("mae","mae_label",T.badge_mae,T.success),("cv","cv_label",T.badge_cv,T.warning),("data","samples_label",T.badge_data,T.text_muted)]):
            tile=MetricTile(self._metrics_grid,T,label=self._s(lk),value="…",badge_bg=bg,value_color=col,fonts=F)
            r,c=divmod(i,2); tile.grid(row=r,column=c,padx=(0 if c==0 else 6),pady=(0 if r==0 else 6),sticky="ew"); self._metric_tiles[key]=tile
        self._metrics_grid.columnconfigure(0,weight=1); self._metrics_grid.columnconfigure(1,weight=1)
        Divider(inner,T).pack(fill="x",pady=14)
        self._result_card=Card(inner,T,padx=16,pady=14); self._result_card.pack(fill="x")
        self._est_lbl=tk.Label(self._result_card,text=self._s("est_price"),font=F["tiny"],fg=T.text_dim,bg=T.result_bg,anchor="center")
        self._price_lbl=tk.Label(self._result_card,textvariable=self._price_var,font=F["mono_xl"],fg=T.price_color,bg=T.result_bg,anchor="center")
        self._hint_lbl=tk.Label(self._result_card,textvariable=self._range_var,font=F["small"],fg=T.text_muted,bg=T.result_bg,wraplength=240,anchor="center")
        self._conf_lbl=tk.Label(self._result_card,text=self._s("confidence"),font=F["tiny"],fg=T.text_dim,bg=T.result_bg,anchor="center")
        self._bar_canvas=tk.Canvas(self._result_card,height=4,bg=T.result_bg,highlightthickness=0)
        for w in [self._est_lbl,self._price_lbl,self._hint_lbl,self._conf_lbl,self._bar_canvas]:
            w.pack(fill="x",pady=(0,3))
        self._range_var.set(self._s("enter_hint")); self._bar_canvas.bind("<Configure>",self._draw_bar)
        Divider(inner,T).pack(fill="x",pady=14)
        self._btn_estimate=PrimaryButton(inner,T,text=self._s("btn_estimate"),command=self._on_predict,fonts=F); self._btn_estimate.pack(fill="x",pady=(0,6))
        row2=tk.Frame(inner,bg=T.sidebar_bg); row2.pack(fill="x")
        self._btn_reset=GhostButton(row2,T,text=self._s("btn_reset"),command=self._on_reset,fonts=F); self._btn_reset.pack(side="left",expand=True,fill="x",padx=(0,4))
        rt_img = self._icons.get("retrain")
        self._btn_retrain=GhostButton(row2,T,text=self._s("btn_retrain") if rt_img else "⟳ "+self._s("btn_retrain"),
                                      image=rt_img if rt_img else "", compound="left" if rt_img else "none",
                                      command=self._on_retrain,fonts=F); self._btn_retrain.pack(side="left",expand=True,fill="x",padx=(4,0))
        tk.Frame(inner,bg=T.sidebar_bg).pack(expand=True,fill="both")
        self._footer_lbl=tk.Label(inner,text=self._s("footer"),font=F["tiny"],fg=T.text_dim,bg=T.sidebar_bg,wraplength=256); self._footer_lbl.pack(anchor="w")
        self._source_lbl=tk.Label(inner,text=self._s("data_source"),font=F["tiny"],fg=T.text_dim,bg=T.sidebar_bg,wraplength=256); self._source_lbl.pack(anchor="w",pady=(2,0))
        vd=Divider(parent,T,orient="v"); vd.pack(side="left",fill="y"); self._vdividers=[vd]
        self._form_outer=tk.Frame(parent,bg=T.bg); self._form_outer.pack(side="left",fill="both",expand=True)
        self._build_form_scroll(self._form_outer)

    def _build_form_scroll(self,parent):
        T=self._theme
        canvas=tk.Canvas(parent,bg=T.bg,highlightthickness=0)
        scrollbar=tk.Scrollbar(parent,orient="vertical",command=canvas.yview)
        self._scroll_canvas=canvas; self._scrollbar=scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right",fill="y"); canvas.pack(side="left",fill="both",expand=True)
        self._form_frame=tk.Frame(canvas,bg=T.bg)
        self._canvas_win=canvas.create_window((0,0),window=self._form_frame,anchor="nw")
        self._form_frame.bind("<Configure>",lambda _:canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",lambda e:canvas.itemconfig(self._canvas_win,width=e.width))
        canvas.bind("<MouseWheel>",lambda e:canvas.yview_scroll(int(-1*(e.delta/120)),"units"))
        canvas.bind("<Button-4>",lambda e:canvas.yview_scroll(-1,"units"))
        canvas.bind("<Button-5>",lambda e:canvas.yview_scroll(1,"units"))
        self._form_inner=tk.Frame(self._form_frame,bg=T.bg,padx=28,pady=22)
        self._form_inner.pack(fill="both",expand=True)
        self._build_form_content(self._form_inner)

    def _build_form_content(self,parent):
        T=self._theme; F=self._fonts
        self._sec1_lbl=tk.Label(parent,text=self._s("section_property"),font=F["heading"],fg=T.text,bg=T.bg); self._sec1_lbl.pack(anchor="w",pady=(0,14))
        # Card 1: basic measurements
        c1=Card(parent,T,padx=22,pady=18); c1.pack(fill="x",pady=(0,12)); self._nums_card=c1
        lbl1=tk.Label(c1,text=self._s("section_nums"),font=F["subhead"],fg=T.accent,bg=T.surface); lbl1.pack(anchor="w",pady=(0,12)); self._nums_inner_lbl=lbl1
        g1=tk.Frame(c1,bg=T.surface); g1.pack(fill="x"); self._nums_grid=g1
        basic_fields=[
            ("f_area","area","entry","120"),
            ("f_bedrooms","bedrooms","combo",["1","2","3","4","5","6","7","8"]),
            ("f_bathrooms","bathrooms","combo",["1","2","3","4","5","6"]),
            ("f_floor","floor","combo",["0","1","2","3","4","5","6","7","8","9","10","11","12","15","18","20","24"]),
            ("f_parking","parking","combo",["0","1","2","3"]),
            ("f_age","building_age","combo",["0","1","2","3","5","7","10","15","20","25","30","40","45"]),
        ]
        for i,(lk,key,wt,opts) in enumerate(basic_fields):
            cell=tk.Frame(g1,bg=T.surface); cell.grid(row=i//3,column=i%3,sticky="nw",padx=(0,24),pady=(0,10))
            lbl=tk.Label(cell,text=self._s(lk),font=F["small"],fg=T.text_muted,bg=T.surface); lbl.pack(anchor="w")
            if wt=="entry":
                var=tk.StringVar(value=opts); w=FlatEntry(cell,T,width=12,textvariable=var,font=F["body"]); w.pack(anchor="w",pady=(3,0))
                self._input_vars[key]=var; self._entry_refs.append((key,w,lbl,lk))
            else:
                w=FlatCombo(cell,opts,T,width=12,font=F["body"]); w.set(opts[1] if len(opts)>1 else opts[0]); w.pack(anchor="w",pady=(3,0))
                self._input_vars[key]=w; self._combo_refs.append((key,w,lbl,lk,opts))
                if key=="bedrooms": w.bind("<<ComboboxSelected>>",lambda e:self.after(10,self._on_bedrooms_change))
        # Card 2: quality
        c2=Card(parent,T,padx=22,pady=18); c2.pack(fill="x",pady=(0,12)); self._quality_card=c2
        lbl2=tk.Label(c2,text=self._s("section_quality"),font=F["subhead"],fg=T.accent,bg=T.surface); lbl2.pack(anchor="w",pady=(0,12)); self._quality_lbl=lbl2
        g2=tk.Frame(c2,bg=T.surface); g2.pack(fill="x"); self._quality_grid=g2
        quality_fields=[
            ("f_condition","condition","combo",["Needs Renovation","Fair","Good","New","Excellent"]),
            ("f_finishing","finishing","combo",["Core & Shell","Semi Finished","Fully Finished"]),
            ("f_furnished","furnished","combo",["Unfurnished","Partially Furnished","Furnished"]),
            ("f_view","view","combo",["Street","City","Garden","Pool","Sea/Lake"]),
        ]
        for i,(lk,key,wt,opts) in enumerate(quality_fields):
            cell=tk.Frame(g2,bg=T.surface); cell.grid(row=0,column=i,sticky="nw",padx=(0,24),pady=(0,0))
            lbl=tk.Label(cell,text=self._s(lk),font=F["small"],fg=T.text_muted,bg=T.surface); lbl.pack(anchor="w")
            w=FlatCombo(cell,opts,T,width=16,font=F["body"])
            defaults={"condition":"Good","finishing":"Fully Finished","furnished":"Unfurnished","view":"Street"}
            w.set(defaults.get(key,opts[0])); w.pack(anchor="w",pady=(3,0))
            self._input_vars[key]=w; self._combo_refs.append((key,w,lbl,lk,opts))
        # Card 3: amenities toggles
        c3=Card(parent,T,padx=22,pady=18); c3.pack(fill="x"); self._amenity_card=c3
        lbl3=tk.Label(c3,text=self._s("section_amenity"),font=F["subhead"],fg=T.accent,bg=T.surface); lbl3.pack(anchor="w",pady=(0,12)); self._amenity_inner_lbl=lbl3
        g3=tk.Frame(c3,bg=T.surface); g3.pack(fill="x"); self._tog_grid=g3
        amenities=[("f_pool","has_pool"),("f_gym","has_gym"),("f_security","has_security"),
                   ("f_elevator","has_elevator"),("f_balcony","has_balcony"),("f_compound","is_compound")]
        from ui.widgets import ToggleSwitch
        for i,(lk,key) in enumerate(amenities):
            cell=tk.Frame(g3,bg=T.surface); cell.grid(row=i//3,column=i%3,sticky="nw",padx=(0,28),pady=(0,8))
            var=tk.IntVar(value=1 if key in ["has_security","has_elevator","has_balcony"] else 0)
            self._input_vars[key]=var; row_f=tk.Frame(cell,bg=T.surface); row_f.pack(anchor="w")
            tog=ToggleSwitch(row_f,variable=var,theme=T,bg=T.surface); tog.pack(side="left")
            lbl=tk.Label(row_f,text=self._s(lk),font=F["body"],fg=T.text,bg=T.surface); lbl.pack(side="left",padx=(8,0))
            self._toggle_refs=getattr(self,"_toggle_refs",[]); self._toggle_refs.append((key,tog,lbl,lk))
        # Card 4: location
        c4=Card(parent,T,padx=22,pady=18); c4.pack(fill="x",pady=(12,0)); self._loc_card=c4
        lbl4=tk.Label(c4,text=self._s("f_location"),font=F["subhead"],fg=T.accent,bg=T.surface); lbl4.pack(anchor="w",pady=(0,10)); self._loc_inner_lbl=lbl4
        sr=tk.Frame(c4,bg=T.surface); sr.pack(fill="x",pady=(0,8))
        self._loc_search_var=tk.StringVar()
        self._loc_search_entry=FlatEntry(sr,T,width=32,textvariable=self._loc_search_var,font=F["body"]); self._loc_search_entry.pack(side="left")
        sh_img = self._icons.get("search")
        self._loc_hint=tk.Label(sr,text=self._s("search_hint") if sh_img else "🔍  "+self._s("search_hint"), 
                                image=sh_img if sh_img else "", compound="left" if sh_img else "none",
                                font=F["tiny"],fg=T.text_dim,bg=T.surface); self._loc_hint.pack(side="left",padx=(10,0))
        lbf=tk.Frame(c4,bg=T.surface); lbf.pack(fill="x")
        self._loc_sb=tk.Scrollbar(lbf,orient="vertical")
        self._loc_listbox=tk.Listbox(lbf,font=F["body"],bg=T.surface2,fg=T.text,
                                     selectbackground=T.accent,selectforeground=T.accent_text,
                                     activestyle="none",highlightthickness=1,
                                     highlightbackground=T.border,highlightcolor=T.accent,
                                     relief="flat",height=7,yscrollcommand=self._loc_sb.set,exportselection=False)
        self._loc_sb.config(command=self._loc_listbox.yview)
        self._loc_listbox.pack(side="left",fill="x",expand=True); self._loc_sb.pack(side="left",fill="y")
        self._loc_search_var.trace_add("write",self._filter_locations)

    # ── Chat page ─────────────────────────────────────────────────
    def _build_chat_page(self,parent):
        T=self._theme; F=self._fonts
        # Header bar
        header=tk.Frame(parent,bg=T.surface,highlightthickness=1,highlightbackground=T.border)
        header.pack(fill="x",side="top")
        bot_img = self._icons.get("bot")
        tk.Label(header,text=" HomeVal AI Assistant" if bot_img else "🤖 HomeVal AI Assistant",
                 image=bot_img if bot_img else "", compound="left" if bot_img else "none",
                 font=F["subhead"],fg=T.text,bg=T.surface).pack(side="left",padx=16,pady=12)
        
        self._chat_nodes=[] # to keep track for themes
        
        # Chat area
        chat_frame=tk.Frame(parent,bg=T.bg); chat_frame.pack(fill="both",expand=True,padx=0,pady=0)
        self._chat_canvas=tk.Canvas(chat_frame,bg=T.bg,highlightthickness=0)
        chat_sb=tk.Scrollbar(chat_frame,orient="vertical",command=self._chat_canvas.yview); self._chat_vsb=chat_sb
        self._chat_canvas.configure(yscrollcommand=chat_sb.set)
        chat_sb.pack(side="right",fill="y"); self._chat_canvas.pack(fill="both",expand=True)
        self._chat_messages_frame=tk.Frame(self._chat_canvas,bg=T.bg,pady=10)
        self._chat_win=self._chat_canvas.create_window((0,0),window=self._chat_messages_frame,anchor="nw")
        
        self._chat_messages_frame.bind("<Configure>",lambda _:self._chat_canvas.configure(scrollregion=self._chat_canvas.bbox("all")))
        self._chat_canvas.bind("<Configure>",lambda e:self._chat_canvas.itemconfig(self._chat_win,width=e.width))
        self._chat_canvas.bind("<MouseWheel>",lambda e:self._chat_canvas.yview_scroll(int(-1*(e.delta/120)),"units"))
        
        # Welcome message
        self._add_chat_bubble("assistant","👋 Welcome to HomeVal AI! I'm your real estate expert. Ask me anything about property prices, neighborhoods, investment advice, or market trends in Egypt.")
        
        # Modern Input bar
        input_container=tk.Frame(parent,bg=T.surface,highlightthickness=1,highlightbackground=T.border)
        input_container.pack(fill="x",side="bottom")
        input_inner=tk.Frame(input_container,bg=T.surface2,highlightthickness=1,highlightbackground=T.border)
        input_inner.pack(fill="both",expand=True,padx=16,pady=12)
        
        self._chat_input=tk.Text(input_inner,height=2,font=F["body"],bg=T.surface2,fg=T.text,
                                  insertbackground=T.accent,relief="flat",wrap="word",
                                  highlightthickness=0)
        self._chat_input.pack(side="left",fill="both",expand=True,padx=12,pady=8)
        self._chat_input.bind("<Return>",self._on_chat_enter)
        self._chat_input.bind("<Shift-Return>",lambda e:"break")
        
        sd_img = self._icons.get("send")
        send_btn=PrimaryButton(input_inner,T,text="" if sd_img else " ➤ ",
                               image=sd_img if sd_img else "",
                               command=self._on_chat_send,fonts=F)
        send_btn.pack(side="right",padx=(0,6),pady=6); self._send_btn=send_btn

    def _add_chat_bubble(self,role:str,text:str):
        T=self._theme; F=self._fonts
        is_user=(role=="user")
        
        # Outer container row for the message
        row_frame=tk.Frame(self._chat_messages_frame,bg=T.bg); row_frame.pack(fill="x",padx=16,pady=8)
        
        # Avatar (emoji based)
        av_img = self._icons.get("user") if is_user else self._icons.get("bot")
        av_text="👤" if is_user else "🤖"
        av_bg=T.surface2 if is_user else T.header_bg
        av_fg=T.accent if is_user else T.text
        
        av_lbl=tk.Label(row_frame,text="" if av_img else av_text,
                        image=av_img if av_img else "",
                        font=F["subhead"],bg=av_bg,fg=av_fg,width=3 if not av_img else 0,height=1 if not av_img else 0)
        av_lbl.pack(side="right" if is_user else "left", anchor="n")
        
        bg   =T.accent    if is_user else T.surface2
        fg   =T.accent_text if is_user else T.text
        align="e"         if is_user else "w"
        
        # Bubble Container
        bubble=tk.Frame(row_frame,bg=bg,highlightthickness=0)
        bubble.pack(side="right" if is_user else "left", padx=(12,12), ipady=4, anchor="n")
        
        lbl=tk.Label(bubble,text=text,font=F["body"],fg=fg,bg=bg,
                     wraplength=650,justify="left",anchor="nw")
        lbl.pack(padx=14,pady=10)
        
        # Time stamp placeholder for extra realism
        from datetime import datetime
        time_str = datetime.now().strftime("%I:%M %p")
        time_lbl=tk.Label(row_frame,text=time_str,font=F["tiny"],fg=T.text_dim,bg=T.bg)
        time_lbl.pack(side="right" if is_user else "left", anchor="s", pady=2)
        
        # Track for themes (for dynamic dark/light toggles)
        self._chat_nodes.append((is_user,row_frame,av_lbl,bubble,lbl,time_lbl))
        
        self._chat_canvas.update_idletasks()
        self._chat_canvas.yview_moveto(1.0)

    def _on_chat_enter(self,event):
        if event.state & 0x1:  # Shift held
            return
        self._on_chat_send(); return "break"

    def _on_chat_send(self):
        text=self._chat_input.get("1.0","end").strip()
        if not text: return
        self._chat_input.delete("1.0","end")
        self._add_chat_bubble("user",text)
        self._chat_history.append({"role":"user","content":text})
        self._send_btn.configure(state="disabled",text="…")
        threading.Thread(target=self._groq_call,daemon=True).start()

    def _groq_call(self):
        key=self._groq_key.get().strip()
        if not key:
            self.after(0,lambda:self._add_chat_bubble("assistant","⚠ Please configure your Groq API key in the .env file."))
            sd_img = self._icons.get("send")
            self.after(0,lambda:self._send_btn.configure(state="normal",text="" if sd_img else " ➤ ")); return
        
        url="https://api.groq.com/openai/v1/chat/completions"
        messages=[{"role":"system","content":CHAT_SYSTEM}]
        
        # Mapping chat history from previous generic format to OpenAI style
        for msg in self._chat_history[-20:]:
            role = "assistant" if msg["role"] == "model" else "user"
            content = msg.get("content", msg.get("parts", [{"text": ""}])[0].get("text", ""))
            messages.append({"role": role, "content": content})
            
        body=_json.dumps({
            "model": GROQ_MODEL,
            "messages": messages
        }).encode()
        
        req=urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {key}")
        req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        
        try:
            with urllib.request.urlopen(req,timeout=30) as resp:
                data=_json.loads(resp.read())
            reply=data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            err=e.read().decode()
            try:
                err_msg = _json.loads(err).get('error',{}).get('message','Unknown')
            except Exception:
                err_msg = err or "Unknown error"
            reply=f"API error {e.code}: {err_msg}"
        except Exception as e:
            reply=f"Error: {e}"
        
        self._chat_history.append({"role":"model","content":reply})
        self.after(0,lambda:self._add_chat_bubble("assistant",reply))
        sd_img = self._icons.get("send")
        self.after(0,lambda:self._send_btn.configure(state="normal",text="" if sd_img else " ➤ "))

    # ── Tab routing ───────────────────────────────────────────────
    def _switch_tab(self,tab_id:str):
        self._active_tab=tab_id; T=self._theme; F=self._fonts
        for tid,btn in self._tab_btns.items():
            active=tid==tab_id
            btn.configure(fg=T.accent if active else T.text_muted,
                          font=(F["body"][0],F["body"][1],"bold") if active else F["body"])
        if tab_id=="estimator": self._estimator_page.lift()
        elif tab_id=="analytics":
            self._analytics_page_holder.lift()
            if self._analytics_widget is None and not self._loading:
                self._build_analytics_widget()
        else: self._chat_page.lift()

    def _build_analytics_widget(self):
        if self._analytics_widget: return
        aw=AnalyticsPage(self._analytics_page_holder,self._pipeline,self._theme,self._lang)
        aw.place(relx=0,rely=0,relwidth=1,relheight=1); self._analytics_widget=aw; aw.build()

    # ── Model load ────────────────────────────────────────────────
    def _load_model_async(self):
        def _w():
            self._pipeline=HousingPipeline()
            self.after(0,self._on_model_ready)
        threading.Thread(target=_w,daemon=True).start()

    def _on_model_ready(self):
        self._loading=False; m=self._pipeline.metrics
        self._loading_lbl.pack_forget(); self._metrics_grid.pack(fill="x")
        for k,v in [("r2",f"{m.r2:.3f}"),("mae",f"E£{m.mae/1e6:.2f}M"),("cv",f"{m.cv_r2_mean:.3f}"),("data",f"{m.n_train+m.n_test:,}")]:
            self._metric_tiles[k].update_value(v)
        self._populate_locations()
        self._status_var.set(f"✓  Model ready  ·  R² {m.r2:.3f}  ·  MAE E£{m.mae/1e6:.2f}M  ·  {len(self._pipeline.locations)} locations")
        if self._active_tab=="analytics": self._build_analytics_widget()

    # ── Location ──────────────────────────────────────────────────
    def _populate_locations(self):
        self._refresh_listbox(self._pipeline.locations)
    def _refresh_listbox(self,locs):
        self._loc_listbox.delete(0,tk.END)
        for l in locs: self._loc_listbox.insert(tk.END,l)
        try: idx=locs.index("Maadi"); self._loc_listbox.selection_set(idx); self._loc_listbox.see(idx)
        except ValueError:
            if locs: self._loc_listbox.selection_set(0)
    def _filter_locations(self,*_):
        q=self._loc_search_var.get().lower().strip()
        locs=self._pipeline.locations if self._pipeline else []
        self._refresh_listbox([l for l in locs if q in l.lower()] if q else locs)
    def _get_selected_location(self):
        sel=self._loc_listbox.curselection()
        return self._loc_listbox.get(sel[0]) if sel else None

    # ── Actions ───────────────────────────────────────────────────
    _BED_AREA={1:75,2:120,3:175,4:260,5:350,6:410,7:470,8:500}
    def _on_bedrooms_change(self):
        try:
            beds=int(self._input_vars["bedrooms"].get()); sug=self._BED_AREA.get(beds,beds*60)
            av=self._input_vars["area"]
            try:
                cur=float(av.get())
                if cur in self._BED_AREA.values() or cur==120: av.set(str(sug))
            except ValueError: av.set(str(sug))
        except Exception: pass

    def _gather_input(self)->PredictionInput:
        area=float(self._input_vars["area"].get() or 0)
        if area<=0: raise ValueError(self._s("err_area"))
        beds=int(self._input_vars["bedrooms"].get())
        baths=int(self._input_vars["bathrooms"].get())
        loc=self._get_selected_location()
        if not loc: raise ValueError(self._s("err_location"))
        return PredictionInput(
            area=area,bedrooms=beds,bathrooms=baths,location=loc,
            condition=self._input_vars["condition"].get(),
            finishing=self._input_vars["finishing"].get(),
            furnished=self._input_vars["furnished"].get(),
            view=self._input_vars["view"].get(),
            floor=int(self._input_vars["floor"].get()),
            building_age=int(self._input_vars["building_age"].get()),
            parking=int(self._input_vars["parking"].get()),
            has_pool=self._input_vars["has_pool"].get(),
            has_gym=self._input_vars["has_gym"].get(),
            has_security=self._input_vars["has_security"].get(),
            has_elevator=self._input_vars["has_elevator"].get(),
            has_balcony=self._input_vars["has_balcony"].get(),
            is_compound=self._input_vars["is_compound"].get(),
        )

    def _on_predict(self):
        if self._loading: messagebox.showinfo("",self._s("loading")); return
        try:
            inp=self._gather_input(); result=self._pipeline.predict(inp)
            self._price_var.set(result.formatted); self._range_var.set(f"{self._s('range_prefix')}:  {result.range_str}")
            self._bar_pct=min(result.price/15_000_000,1.0); self._draw_bar()
            self._status_var.set(f"Predicted: {result.formatted}  ·  {inp.location}  ·  {inp.area}m²  ·  {inp.bedrooms}bd  ·  {inp.condition}")
            self._save_prediction_to_csv(inp, result)
        except ValueError as e: messagebox.showerror(self._s("err_input"),str(e))
        except Exception as e: messagebox.showerror("Error",str(e))

    def _save_prediction_to_csv(self, inp, result):
        import csv, uuid, datetime
        from pathlib import Path
        csv_file = Path(__file__).resolve().parent.parent / "assets" / "egypt_home_pricing_30k.csv"
        prop_id = f"USR-{uuid.uuid4().hex[:6].upper()}"
        year_built = datetime.datetime.now().year - inp.building_age
        row = [
            prop_id, inp.location, "Apartment", inp.condition, inp.finishing,
            inp.furnished, inp.view, int(inp.area), inp.bedrooms, inp.bathrooms,
            inp.floor, inp.building_age, year_built, inp.parking,
            inp.has_pool, inp.has_gym, inp.has_security, inp.has_elevator,
            inp.has_balcony, inp.is_compound, inp.garden_sqm,
            inp.height_m, inp.dist_center, inp.dist_metro,
            0, 0, 1.0, 1.0, int(result.price), int(result.price)
        ]
        def _write():
            try:
                with open(csv_file, "a", newline="", encoding="utf-8") as f:
                    csv.writer(f).writerow(row)
            except Exception as e:
                print(f"Error appending prediction to CSV: {e}")
        import threading
        threading.Thread(target=_write, daemon=True).start()

    def _on_reset(self):
        self._price_var.set("—"); self._range_var.set(self._s("enter_hint"))
        self._bar_pct=0.0; self._draw_bar(); self._loc_search_var.set("")
        self._status_var.set(self._s("ready"))

    def _on_retrain(self):
        if self._loading: return
        self._status_var.set("⟳  Retraining model…")
        def _w():
            self._pipeline.retrain()
            self.after(0,lambda:[self._on_model_ready(),messagebox.showinfo(self._s("retrain_title"),self._s("retrain_done"))])
        threading.Thread(target=_w,daemon=True).start()

    # ── Theme / Lang ──────────────────────────────────────────────
    def _toggle_theme(self):
        new="light" if self._theme.name=="dark" else "dark"
        self._theme=THEMES[new]; self._apply_theme_colors()
        if self._analytics_widget: self._analytics_widget.apply_theme(self._theme)

    def _toggle_lang(self):
        self._lang="ar" if self._lang=="en" else "en"; self._fonts=get_fonts(self._lang); self._rebuild_text()

    def _apply_theme_colors(self):
        T=self._theme; F=self._fonts
        self.configure(bg=T.bg)
        self._topbar.configure(bg=T.header_bg,highlightbackground=T.header_bdr)
        self._repaint(self._topbar,T.header_bg)
        self._app_name_lbl.configure(fg=T.text); self._dot.configure(bg=T.header_bg); self._dot.itemconfig("dot",fill=T.accent)
        is_dark = T.name=="dark"
        ti="☀  " if is_dark else "☾  "; tt=self._s("theme_light") if is_dark else self._s("theme_dark")
        img = self._icons.get("theme_light" if is_dark else "theme_dark")
        self._theme_btn.configure(text=tt if img else ti+tt, image=img if img else "", compound="left" if img else "none")
        self._lang_btn.configure(text=self._s("lang_toggle"))
        for b in [self._theme_btn,self._lang_btn]: b.apply_theme(T)
        for d in self._toolbar_dividers: d.apply_theme(T)
        for tid,btn in self._tab_btns.items():
            btn.configure(bg=T.header_bg,fg=T.accent if tid==self._active_tab else T.text_muted,activebackground=T.surface2)
        self._statusbar.configure(bg=T.surface2,highlightbackground=T.border)
        self._status_lbl.configure(bg=T.surface2,fg=T.text_dim); self._subtitle_lbl.configure(bg=T.surface2,fg=T.text_dim)
        self._pages.configure(bg=T.bg); self._estimator_page.configure(bg=T.bg)
        self._analytics_page_holder.configure(bg=T.bg); self._chat_page.configure(bg=T.bg)
        self._sidebar.configure(bg=T.sidebar_bg); self._repaint(self._sidebar,T.sidebar_bg)
        self._metrics_title.configure(bg=T.sidebar_bg,fg=T.text_muted); self._loading_lbl.configure(bg=T.sidebar_bg,fg=T.text_dim)
        self._footer_lbl.configure(bg=T.sidebar_bg,fg=T.text_dim); self._source_lbl.configure(bg=T.sidebar_bg,fg=T.text_dim)
        self._metrics_grid.configure(bg=T.sidebar_bg)
        for k,(bg,col) in {"r2":(T.badge_r2,T.accent),"mae":(T.badge_mae,T.success),"cv":(T.badge_cv,T.warning),"data":(T.badge_data,T.text_muted)}.items():
            if k in self._metric_tiles: self._metric_tiles[k].apply_theme(T,bg,col)
        self._result_card.configure(bg=T.result_bg,highlightbackground=T.result_bdr)
        for w in [self._est_lbl,self._price_lbl,self._hint_lbl,self._conf_lbl,self._bar_canvas]: w.configure(bg=T.result_bg)
        self._est_lbl.configure(fg=T.text_dim); self._price_lbl.configure(fg=T.price_color); self._hint_lbl.configure(fg=T.text_muted); self._conf_lbl.configure(fg=T.text_dim); self._draw_bar()
        for b in [self._btn_estimate,self._btn_reset,self._btn_retrain]: b.apply_theme(T)
        for d in self._vdividers: d.apply_theme(T)
        for w in [self._form_outer,self._form_frame,self._form_inner]: w.configure(bg=T.bg)
        self._scroll_canvas.configure(bg=T.bg); self._scrollbar.configure(bg=T.scroll_bg,troughcolor=T.surface2)
        self._sec1_lbl.configure(bg=T.bg,fg=T.text)
        for card in [self._nums_card,self._quality_card,self._amenity_card,self._loc_card]:
            try: card.apply_theme(T)
            except: pass
        for grid in [self._nums_grid,self._quality_grid,self._tog_grid]:
            try: grid.configure(bg=T.surface)
            except: pass
        for _,w,lbl,_ in self._entry_refs:
            w.apply_theme(T); lbl.configure(bg=T.surface,fg=T.text_muted); lbl.master.configure(bg=T.surface)
        for _,w,lbl,_,_ in self._combo_refs:
            w.apply_theme(T); lbl.configure(bg=T.surface,fg=T.text_muted); lbl.master.configure(bg=T.surface)
        for _,tog,lbl,_ in getattr(self,"_toggle_refs",[]):
            tog.apply_theme(T,bg=T.surface); lbl.configure(bg=T.surface,fg=T.text); lbl.master.configure(bg=T.surface); tog.master.master.configure(bg=T.surface)
        self._loc_inner_lbl.configure(bg=T.surface,fg=T.accent); self._loc_inner_lbl.master.configure(bg=T.surface)
        self._loc_search_entry.apply_theme(T); self._loc_search_entry.master.configure(bg=T.surface)
        self._loc_hint.configure(bg=T.surface,fg=T.text_dim)
        self._loc_listbox.configure(bg=T.surface2,fg=T.text,selectbackground=T.accent,selectforeground=T.accent_text,highlightbackground=T.border,highlightcolor=T.accent)
        self._loc_sb.configure(bg=T.scroll_bg,troughcolor=T.surface2); self._loc_listbox.master.configure(bg=T.surface)
        
        # Chat Nodes Update
        if hasattr(self, "_chat_nodes"):
            for is_user, row, av, bub, txt, tm in self._chat_nodes:
                row.configure(bg=T.bg)
                av.configure(bg=T.surface2 if is_user else T.header_bg, fg=T.accent if is_user else T.text)
                bub.configure(bg=T.accent if is_user else T.surface2)
                txt.configure(bg=T.accent if is_user else T.surface2, fg=T.accent_text if is_user else T.text)
                tm.configure(bg=T.bg, fg=T.text_dim)
        
        if hasattr(self, "_chat_canvas"):
            self._chat_canvas.configure(bg=T.bg)
            self._chat_messages_frame.configure(bg=T.bg)

    def _rebuild_text(self):
        T=self._theme; F=self._fonts
        self._app_name_lbl.configure(text=self._s("app_name"),font=F["display"])
        self._lang_btn.configure(text=self._s("lang_toggle"))
        is_dark = T.name=="dark"
        ti="☀  " if is_dark else "☾  "; tt=self._s("theme_light") if is_dark else self._s("theme_dark")
        img = self._icons.get("theme_light" if is_dark else "theme_dark")
        self._theme_btn.configure(text=tt if img else ti+tt, image=img if img else "", compound="left" if img else "none")
        self._subtitle_lbl.configure(text=self._s("app_subtitle"),font=F["tiny"])
        for tid,btn in self._tab_btns.items():
            lk={"estimator":"tab_estimator","analytics":"tab_analytics","chat":"tab_chat"}[tid]
            ic={"estimator":"🏠","analytics":"📊","chat":"💬"}[tid]
            bimg = self._icons.get(tid)
            btn.configure(text=f" {self._s(lk)} " if bimg else f"  {ic}  {self._s(lk)}  ",
                          image=bimg if bimg else "", compound="left" if bimg else "none", font=F["body"])
        self._metrics_title.configure(text=self._s("model_metrics"),font=F["subhead"])
        self._loading_lbl.configure(text=self._s("loading"),font=F["small"])
        self._footer_lbl.configure(text=self._s("footer"),font=F["tiny"])
        self._source_lbl.configure(text=self._s("data_source"),font=F["tiny"])
        for k,lk in [("r2","r2_label"),("mae","mae_label"),("cv","cv_label"),("data","samples_label")]:
            if k in self._metric_tiles: self._metric_tiles[k].update_label(self._s(lk))
        self._est_lbl.configure(text=self._s("est_price"),font=F["tiny"])
        self._price_lbl.configure(font=F["mono_xl"]); self._conf_lbl.configure(text=self._s("confidence"),font=F["tiny"])
        if self._bar_pct==0.0: self._range_var.set(self._s("enter_hint"))
        self._btn_estimate.configure(text=self._s("btn_estimate"),font=F["subhead"])
        self._btn_reset.configure(text=self._s("btn_reset"),font=F["body"])
        rt_img = self._icons.get("retrain")
        self._btn_retrain.configure(text=self._s("btn_retrain") if rt_img else "⟳ "+self._s("btn_retrain"),
                                    image=rt_img if rt_img else "", compound="left" if rt_img else "none", font=F["body"])
        self._sec1_lbl.configure(text=self._s("section_property"),font=F["heading"])
        for _,w,lbl,lk in self._entry_refs: lbl.configure(text=self._s(lk),font=F["small"]); w.configure(font=F["body"])
        for _,w,lbl,lk,_ in self._combo_refs: lbl.configure(text=self._s(lk),font=F["small"]); w.configure(font=F["body"])
        for _,tog,lbl,lk in getattr(self,"_toggle_refs",[]): lbl.configure(text=self._s(lk),font=F["body"])
        self._loc_inner_lbl.configure(text=self._s("f_location"),font=F["subhead"])
        self._loc_search_entry.configure(font=F["body"]); self._loc_listbox.configure(font=F["body"])
        sh_img = self._icons.get("search")
        self._loc_hint.configure(text=self._s("search_hint") if sh_img else "🔍  "+self._s("search_hint"),
                                 image=sh_img if sh_img else "", compound="left" if sh_img else "none", font=F["tiny"])

    # ── Utils ─────────────────────────────────────────────────────
    def _s(self,key): return STRINGS[self._lang].get(key,key)
    def _repaint(self,w,bg):
        try: w.configure(bg=bg)
        except: pass
        for c in w.winfo_children(): self._repaint(c,bg)
    def _center(self):
        self.update_idletasks(); w=self.winfo_width(); h=self.winfo_height()
        sw=self.winfo_screenwidth(); sh=self.winfo_screenheight()
        self.geometry(f"+{(sw-w)//2}+{(sh-h)//2}")
    def _draw_bar(self,_=None):
        c=self._bar_canvas; T=self._theme; c.delete("all"); W=c.winfo_width() or 260
        c.create_rectangle(0,0,W,4,fill=T.border,outline="")
        if self._bar_pct>0: c.create_rectangle(0,0,int(W*self._bar_pct),4,fill=T.accent,outline="")
