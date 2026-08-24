import os

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(ROOT, "assets")
OUTPUT_DIR = os.path.join(ROOT, "output")
SCENES_DIR = os.path.join(OUTPUT_DIR, "scenes")

# Create folders
for d in [ASSETS_DIR, OUTPUT_DIR, SCENES_DIR]:
    os.makedirs(d, exist_ok=True)

# Wan 2.2 model ID — change this to whatever model you have access to.
# Examples:
#   "Wan-AI/Wan2.2-I2V-A14B"
#   "Wan-AI/Wan2.1-I2V-A14B"
#   or a local path / quantized version
MODEL_ID = "Wan-AI/Wan2.2-I2V-A14B"

# Available output resolutions for 9:16 vertical
RESOLUTIONS = {
    "360p": (360, 640),
    "480p": (480, 854),
}

DEFAULT_FPS = 16
DEFAULT_GUIDANCE = 5.0
DEFAULT_STEPS = 20