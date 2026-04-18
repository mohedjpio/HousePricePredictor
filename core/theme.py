"""
Theme engine + i18n strings.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

STRINGS: Dict[str, Dict[str, str]] = {
    "en": {
        "app_name":        "HomeVal",
        "app_subtitle":    "AI-Powered Property Valuation",
        "lang_toggle":     "عربي",
        "theme_dark":      "Dark",
        "theme_light":     "Light",
        "model_metrics":   "Model Performance",
        "r2_label":        "R² Score",
        "mae_label":       "Avg. Error",
        "cv_label":        "CV Score",
        "samples_label":   "Dataset",
        "est_price":       "ESTIMATED PRICE",
        "enter_hint":      "Fill in the form and click Estimate",
        "range_prefix":    "Range",
        "confidence":      "Confidence Band  ±12%",
        "btn_estimate":    "Estimate Price",
        "btn_reset":       "Reset",
        "btn_retrain":     "Retrain Model",
        "section_property":"Property Details",
        "f_area":          "Area (m²)",
        "f_bedrooms":      "Bedrooms",
        "f_bathrooms":     "Bathrooms",
        "f_location":      "Location",
        "loading":         "Loading model…",
        "err_input":       "Input Error",
        "err_area":        "Area must be a positive number.",
        "err_location":    "Please select a location.",
        "retrain_done":    "Model retrained successfully.",
        "retrain_title":   "Retrain Complete",
        "footer":          "Trained on 10,000+ Egyptian property listings",
        "data_source":     "Sources: OLX Egypt · RealEstate.eg · Property Finder",
        "tab_chat":        "AI Chat",
        "section_quality": "Quality & Condition",
        "section_nums":    "Measurements & Counts",
        "f_condition":     "Condition",
        "f_finishing":     "Finishing",
        "f_furnished":     "Furnished",
        "f_view":          "View Type",
        "f_floor":         "Floor Number",
        "f_parking":       "Parking Spaces",
        "f_age":           "Building Age (yrs)",
        "f_pool":          "Swimming Pool",
        "f_gym":           "Gym",
        "f_security":      "Security",
        "f_elevator":      "Elevator",
        "f_balcony":       "Balcony",
        "f_compound":      "In Compound",
        "ready":           "Ready",
        "tab_estimator":  "Estimator",
        "tab_analytics":  "Analytics",
        "section_nums":   "Measurements",
        "search_hint":    "type to filter locations",
        "ready":          "Ready",
    },
    "ar": {
        "app_name":        "هوم فال",
        "app_subtitle":    "تقييم العقارات بالذكاء الاصطناعي",
        "lang_toggle":     "English",
        "theme_dark":      "داكن",
        "theme_light":     "فاتح",
        "model_metrics":   "أداء النموذج",
        "r2_label":        "دقة النموذج",
        "mae_label":       "متوسط الخطأ",
        "cv_label":        "التحقق المتقاطع",
        "samples_label":   "حجم البيانات",
        "est_price":       "السعر التقديري",
        "enter_hint":      "أدخل البيانات ثم اضغط تقدير",
        "range_prefix":    "النطاق",
        "confidence":      "نطاق الثقة  ±١٢٪",
        "btn_estimate":    "تقدير السعر",
        "btn_reset":       "إعادة تعيين",
        "btn_retrain":     "إعادة تدريب النموذج",
        "section_property":"تفاصيل العقار",
        "f_area":          "المساحة (م²)",
        "f_bedrooms":      "غرف النوم",
        "f_bathrooms":     "دورات المياه",
        "f_location":      "الموقع",
        "loading":         "جارٍ تحميل النموذج…",
        "err_input":       "خطأ في الإدخال",
        "err_area":        "يجب أن تكون المساحة رقماً موجباً.",
        "err_location":    "الرجاء اختيار الموقع.",
        "retrain_done":    "تم إعادة تدريب النموذج بنجاح.",
        "retrain_title":   "اكتملت إعادة التدريب",
        "footer":          "مدرَّب على أكثر من ١٠٬٠٠٠ إعلان عقاري مصري",
        "data_source":     "المصادر: OLX مصر · RealEstate.eg · Property Finder",
        "tab_chat":        "محادثة AI",
        "section_quality": "الجودة والحالة",
        "section_nums":    "القياسات والأعداد",
        "f_condition":     "حالة العقار",
        "f_finishing":     "نوع التشطيب",
        "f_furnished":     "التأثيث",
        "f_view":          "نوع الإطلالة",
        "f_floor":         "رقم الطابق",
        "f_parking":       "مواقف السيارات",
        "f_age":           "عمر المبنى (سنة)",
        "f_pool":          "حمام سباحة",
        "f_gym":           "صالة رياضية",
        "f_security":      "حراسة أمنية",
        "f_elevator":      "مصعد",
        "f_balcony":       "بلكونة",
        "f_compound":      "داخل كومباوند",
        "ready":           "جاهز",
        "tab_estimator":  "التقدير",
        "tab_analytics":  "التحليلات",
        "section_nums":   "القياسات",
        "search_hint":    "اكتب لتصفية المواقع",
        "ready":          "جاهز",
    },
}


@dataclass
class Theme:
    name: str
    bg: str          = "#F5F7FA"
    surface: str     = "#FFFFFF"
    surface2: str    = "#EEF0F4"
    border: str      = "#DDE1E7"
    border2: str     = "#BEC4CF"
    text: str        = "#0D1117"
    text_muted: str  = "#4B5563"
    text_dim: str    = "#9CA3AF"
    accent: str      = "#1D6AE5"
    accent_hover: str= "#1558C8"
    accent_text: str = "#FFFFFF"
    success: str     = "#0A6640"
    warning: str     = "#92400E"
    error: str       = "#B91C1C"
    tog_off: str     = "#C4C9D4"
    tog_on: str      = "#1D6AE5"
    tog_knob: str    = "#FFFFFF"
    sidebar_bg: str  = "#F0F2F6"
    sidebar_bdr: str = "#DDE1E7"
    result_bg: str   = "#EBF2FF"
    result_bdr: str  = "#93C5FD"
    price_color: str = "#0A6640"
    header_bg: str   = "#FFFFFF"
    header_bdr: str  = "#DDE1E7"
    scroll_bg: str   = "#E2E6EC"
    badge_r2: str    = "#EBF2FF"
    badge_mae: str   = "#ECFDF5"
    badge_cv: str    = "#FFF7ED"
    badge_data: str  = "#F5F3FF"


DARK = Theme(
    name        = "dark",
    bg          = "#0D1117",
    surface     = "#161B22",
    surface2    = "#21262D",
    border      = "#30363D",
    border2     = "#444C56",
    text        = "#E6EDF3",
    text_muted  = "#8B949E",
    text_dim    = "#484F58",
    accent      = "#3B82F6",
    accent_hover= "#60A5FA",
    accent_text = "#FFFFFF",
    success     = "#3FB950",
    warning     = "#D29922",
    error       = "#F85149",
    tog_off     = "#444C56",
    tog_on      = "#3B82F6",
    tog_knob    = "#FFFFFF",
    sidebar_bg  = "#161B22",
    sidebar_bdr = "#30363D",
    result_bg   = "#1C2A3A",
    result_bdr  = "#2D4A6E",
    price_color = "#3FB950",
    header_bg   = "#161B22",
    header_bdr  = "#30363D",
    scroll_bg   = "#21262D",
    badge_r2    = "#1C2A3A",
    badge_mae   = "#162820",
    badge_cv    = "#2A2010",
    badge_data  = "#1E1A2E",
)

LIGHT = Theme(
    name        = "light",
    bg          = "#F5F7FA",
    surface     = "#FFFFFF",
    surface2    = "#EEF0F4",
    border      = "#DDE1E7",
    border2     = "#BEC4CF",
    text        = "#0D1117",
    text_muted  = "#4B5563",
    text_dim    = "#9CA3AF",
    accent      = "#1D6AE5",
    accent_hover= "#1558C8",
    accent_text = "#FFFFFF",
    success     = "#0A6640",
    warning     = "#92400E",
    error       = "#B91C1C",
    tog_off     = "#C4C9D4",
    tog_on      = "#1D6AE5",
    tog_knob    = "#FFFFFF",
    sidebar_bg  = "#F0F2F6",
    sidebar_bdr = "#DDE1E7",
    result_bg   = "#EBF2FF",
    result_bdr  = "#93C5FD",
    price_color = "#0A6640",
    header_bg   = "#FFFFFF",
    header_bdr  = "#DDE1E7",
    scroll_bg   = "#E2E6EC",
    badge_r2    = "#EBF2FF",
    badge_mae   = "#ECFDF5",
    badge_cv    = "#FFF7ED",
    badge_data  = "#F5F3FF",
)

THEMES = {"dark": DARK, "light": LIGHT}

_LATIN_BODY  = ("Calibri", "Helvetica Neue", "DejaVu Sans")
_ARABIC_BODY = ("Segoe UI", "Tahoma", "Arial Unicode MS", "DejaVu Sans")
_MONO        = ("Consolas", "Menlo", "DejaVu Sans Mono")

def get_fonts(lang: str) -> dict:
    base = _ARABIC_BODY if lang == "ar" else _LATIN_BODY
    mono = _MONO
    f = base[0]; m = mono[0]
    return {
        "display":  (f, 22, "bold"),
        "heading":  (f, 12, "bold"),
        "subhead":  (f, 10, "bold"),
        "body":     (f, 10),
        "small":    (f, 9),
        "tiny":     (f, 8),
        "mono_xl":  (m, 30, "bold"),
        "mono_lg":  (m, 14, "bold"),
        "mono":     (m, 10),
    }
