import os

# path database
DATABASE_DIR = os.path.join("database", "projects")
os.makedirs(DATABASE_DIR, exist_ok=True)

# design system
FONT_FAMILY = "Segoe UI"
COLOR_PRIMARY = "#A88686"
COLOR_PRIMARY_DARK = "#8F6E6E"
COLOR_BG_LIGHT = "#F5F2F2"
COLOR_TEXT_DARK = "#2B2626"
COLOR_SUCCESS = "#2ECC71"
COLOR_INFO = "#4A90E2"
COLOR_DANGER = "#E74C3C"
COLOR_DARK_BOX = "#1E1E1E"