"""Central configuration: paths, constants, palettes, and shared text."""
from pathlib import Path

# Paths are built from this file's location so they work locally and on
# Streamlit Community Cloud (where the working directory can differ).
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "Provisional_Natality_2025_CDC1.csv"

APP_TITLE = "U.S. Births in 2025: Provisional CDC Counts"
DATA_YEAR = 2025
CDC_SOURCE_NAME = "Centers for Disease Control and Prevention (CDC)"
CDC_SOURCE_URL = "https://www.cdc.gov/nchs/nvss/births.htm"
DATA_FILE_NAME = DATA_PATH.name

REQUIRED_COLUMNS = [
    "state_of_residence",
    "month",
    "month_code",
    "year_code",
    "sex_of_infant",
    "births",
]

# Chronological month order. Everything that shows months uses these lists,
# so charts, filters, and tables never fall back to alphabetical order.
MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
MONTH_CODE_TO_NAME = {code: name for code, name in enumerate(MONTH_NAMES, start=1)}
MONTH_ABBRS = [name[:3] for name in MONTH_NAMES]
MONTH_CODE_TO_ABBR = {code: name[:3] for code, name in MONTH_CODE_TO_NAME.items()}

SEX_VALUES = ["Female", "Male"]
SEX_OPTIONS = ["Both", *SEX_VALUES]

# Colorblind-safe palette (Okabe-Ito).
PRIMARY_COLOR = "#0072B2"      # blue
SEX_COLORS = {"Female": "#E69F00", "Male": "#0072B2"}  # orange, blue
TOP_COLOR = "#0072B2"
BOTTOM_COLOR = "#D55E00"       # vermillion
SEQUENTIAL_SCALE = "Blues"

PLOTLY_CONFIG = {"displaylogo": False}
