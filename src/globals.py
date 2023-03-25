VERSION = "3.0.1"
FFMPEG_DL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
TITLE = f"Cheezos Video Compressor v{VERSION}"
READY_TEXT = f"Select your videos to get started."
H_GAP = 20
V_GAP = 5
W_SIZE = (250, 350)
W_HALFSIZE = (int(W_SIZE[0] / 2), int(W_SIZE[1] / 2))
B_SIZE = (int(W_SIZE[0] - H_GAP), 50)
SB_SIZE = (int(W_SIZE[0] - H_GAP), 30)
L_FS_SIZE = (W_HALFSIZE[0] - int(H_GAP / 2) - 20, 25)
E_FS_SIZE = (W_HALFSIZE[0] - int(H_GAP / 2) - 20, 25)
L_LOG_SIZE = (int(W_SIZE[0] - H_GAP), 120)
B_SEL_POS = (W_HALFSIZE[0] - int(B_SIZE[0] / 2), V_GAP)
B_COMP_POS = (
    B_SEL_POS[0],
    B_SEL_POS[1] + B_SIZE[1],
)
B_ABORT_POS = (
    B_SEL_POS[0],
    B_COMP_POS[1] + B_SIZE[1],
)
B_FS_POS = (
    W_HALFSIZE[0] - L_FS_SIZE[0],
    B_ABORT_POS[1] + B_SIZE[1] + V_GAP,
)
E_FS_POS = (
    W_HALFSIZE[0],
    B_ABORT_POS[1] + B_SIZE[1] + V_GAP,
)
L_LOG_POS = (B_SEL_POS[0], E_FS_POS[1] + E_FS_SIZE[1] + V_GAP)
B_FOOT_POS = (B_SEL_POS[0], L_LOG_POS[1] + L_LOG_SIZE[1] + V_GAP)
platform = ""
ffmpeg_path = "ffmpeg"
ffprobe_path = "ffprobe"
queue = []
completed = []
dir_root = ""
dir_bin = ""
dir_output = ""
ffmpeg_installed = False
compressing = False
