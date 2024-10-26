# Window dimensions
from src.rect import Rect


WINDOW = Rect(0, 0, 250, 400)
WINDOW_HALF = Rect(0, 0, WINDOW.w // 2, WINDOW.h // 2)

LABEL_STYLE = """
    QLabel {
        qproperty-alignment: AlignCenter;
        padding-bottom: 2px;
    }
"""

LABEL_LOG_STYLE = """
    QLabel {
        qproperty-alignment: AlignCenter;
        border: 1px solid black; 
        border-radius: 5px; 
        margin: 1px;
    }
"""

BUTTON_DISABLED_STYLE = """
    QPushButton {
        background-color: #666666;
        color: #cccccc;
        border: none;
        border-radius: 5px;
    }
"""

BUTTON_SELECT_STYLE = """
    QPushButton {
        background-color: #039dfc;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #0384d5;
        border: 1px solid #026ba9;
    }
    QPushButton:pressed {
        background-color: #026ba9;
        padding: 1px;
    }
"""

BUTTON_COMPRESS_STYLE = """
    QPushButton {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #45a049;
        border: 1px solid #3d8b40;
    }
    QPushButton:pressed {
        background-color: #3d8b40;
        padding: 1px;
    }
"""

BUTTON_ABORT_STYLE = """
    QPushButton {
        background-color: #f44336;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #da190b;
        border: 1px solid #b71c1c;
    }
    QPushButton:pressed {
        background-color: #b71c1c;
        padding: 1px;
    }
"""

PROGRESS_BAR_STYLE = """
    QProgressBar {
        min-height: 25px;
        max-height: 25px;
        border: 1px solid black;
        border-radius: 5px;
        text-align: center;
    }
    QProgressBar::chunk {
        min-height: 25px;
        max-height: 25px;
        border-radius: 5px;
        text-align: center;
        background-color: #4CAF50;
    }
"""

CHECKBOX_STYLE = """
    QCheckBox::indicator {
        width: 25px;
        height: 25px;
    }
"""

LINEEDIT_STYLE = """
    QLineEdit {
        border: 1px solid black;
        border-radius: 5px;
        qproperty-alignment: AlignCenter;
    }
    QLineEdit:focus {
        border: 1px solid black;
    }
    QLineEdit:hover {
        border: 1px solid black;
    }
"""


# Gaps
H_GAP = 5  # Horizontal gap
V_GAP = 5  # Vertical gap

# Buttons and elements
SELECT_BUTTON = Rect(
    H_GAP,  # Start with H_GAP from left
    V_GAP,  # Start with V_GAP from top
    WINDOW.w - (H_GAP * 2),  # Full width minus gaps on both sides
    50,
)

COMPRESS_BUTTON = Rect(
    H_GAP,
    SELECT_BUTTON.y + SELECT_BUTTON.h + V_GAP,
    (WINDOW.w - (H_GAP * 3)) // 2,  # Half width minus gaps
    50,
)

ABORT_BUTTON = Rect(
    COMPRESS_BUTTON.x + COMPRESS_BUTTON.w + H_GAP,
    COMPRESS_BUTTON.y,
    COMPRESS_BUTTON.w,
    COMPRESS_BUTTON.h,
)

FILE_SIZE_LABEL = Rect(
    H_GAP,
    COMPRESS_BUTTON.y + COMPRESS_BUTTON.h + V_GAP,
    (COMPRESS_BUTTON.w // 2) - (H_GAP // 2),
    25,
)

FILE_SIZE_ENTRY = Rect(
    COMPRESS_BUTTON.x + (COMPRESS_BUTTON.w // 2) + (H_GAP // 2),
    FILE_SIZE_LABEL.y,
    COMPRESS_BUTTON.w // 2,
    25,
)

GPU_LABEL = Rect(
    H_GAP,
    FILE_SIZE_LABEL.y + FILE_SIZE_LABEL.h + V_GAP,
    COMPRESS_BUTTON.w // 2,
    25,
)

GPU_CHECKBOX = Rect(
    FILE_SIZE_ENTRY.x + (FILE_SIZE_ENTRY.w // 2) - 12,
    GPU_LABEL.y,
    25,
    25,
)

PROGRESS_BAR = Rect(
    H_GAP,
    WINDOW.h - V_GAP - 25,
    WINDOW.w - (H_GAP * 2),
    25,
)

LOG_AREA = Rect(
    H_GAP,
    GPU_LABEL.y + GPU_LABEL.h + V_GAP,
    WINDOW.w - (H_GAP * 2),
    PROGRESS_BAR.y - (GPU_LABEL.y + GPU_LABEL.h + V_GAP * 2),
)
