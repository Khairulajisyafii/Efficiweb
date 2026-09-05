import os

# Database Path
DATABASE_DIR = os.path.join("database", "projects")
os.makedirs(DATABASE_DIR, exist_ok=True)

GLOBAL_SHORTLINKS_FILE = os.path.join("database", "global_shortlinks.json")
GLOBAL_SNIPPETS_FILE   = os.path.join("database", "global_snippets.json")

# Monochrome Modern Minimalist Theme for CustomTkinter
FONT_FAMILY        = "Segoe UI"
COLOR_BG_MAIN      = "#0C0C0C"   # Deepest black/grey
COLOR_BG_SIDEBAR   = "#141414"   # Slightly lifted black
COLOR_BG_CARD      = "#1E1E1E"   # Card background
COLOR_BG_INPUT     = "#2A2A2A"   # Input fields
COLOR_TEXT_LIGHT   = "#F5F5F5"   # White text
COLOR_TEXT_MUTED   = "#999999"   # Muted grey text
COLOR_ACCENT_CYAN  = "#E0E0E0"   # Light silver/white accent
COLOR_ACCENT_TEAL  = "#888888"   # Dark silver/grey accent
COLOR_DANGER       = "#FF4C4C"   # Red (Destructive Actions)
COLOR_SUCCESS      = "#333333"   # Dark grey for success buttons (or white)