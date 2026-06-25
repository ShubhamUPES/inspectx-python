# ── InspectX / Hestabit DDS — Design Tokens ──────────────────────────────────

DARK_BG        = "#0F0E2A"
SIDEBAR_BORDER = "#1E1B4B"
CONTENT_BG     = "#F1F5F9"
WHITE          = "#FFFFFF"

# Gray scale
GRAY_50  = "#F9FAFB"
GRAY_100 = "#F3F4F6"
GRAY_200 = "#E5E7EB"
GRAY_300 = "#D1D5DB"
GRAY_400 = "#9CA3AF"
GRAY_500 = "#6B7280"
GRAY_600 = "#4B5563"
GRAY_700 = "#374151"
GRAY_900 = "#111827"

# Violet / purple
VIOLET_50  = "#F5F3FF"
VIOLET_100 = "#EDE9FE"
VIOLET_200 = "#DDD6FE"
VIOLET_400 = "#A78BFA"
VIOLET_500 = "#8B5CF6"
VIOLET_600 = "#7C3AED"
VIOLET_700 = "#6D28D9"

# Emerald / green
EMERALD_50  = "#ECFDF5"
EMERALD_200 = "#A7F3D0"
EMERALD_400 = "#34D399"
EMERALD_600 = "#059669"
EMERALD_700 = "#047857"

# Amber / yellow
AMBER_50  = "#FFFBEB"
AMBER_200 = "#FDE68A"
AMBER_600 = "#D97706"

# Red
RED_50  = "#FEF2F2"
RED_200 = "#FECACA"
RED_400 = "#F87171"
RED_600 = "#DC2626"

# Cyan
CYAN_50  = "#ECFEFF"
CYAN_500 = "#06B6D4"
CYAN_600 = "#0891B2"

# Indigo
INDIGO_50  = "#EEF2FF"
INDIGO_600 = "#4F46E5"

# ── Tone map for Badge / MetricCard ──────────────────────────────────────────
TONE: dict[str, dict] = {
    "gray":   {"bg": GRAY_100,    "text": GRAY_700,    "border": GRAY_200},
    "purple": {"bg": VIOLET_100,  "text": VIOLET_700,  "border": VIOLET_200},
    "green":  {"bg": EMERALD_50,  "text": EMERALD_600, "border": EMERALD_200},
    "amber":  {"bg": AMBER_50,    "text": AMBER_600,   "border": AMBER_200},
    "red":    {"bg": RED_50,      "text": RED_600,     "border": RED_200},
    "cyan":   {"bg": CYAN_50,     "text": CYAN_600,    "border": "#A5F3FC"},
    "indigo": {"bg": INDIGO_50,   "text": INDIGO_600,  "border": "#C7D2FE"},
}
