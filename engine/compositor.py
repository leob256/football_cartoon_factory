import os
from PIL import Image
from config import SCENES_DIR

def compose_scene(
    character_path,
    background_path,
    output_dir=None,
    character_scale=0.55,
    vertical_position=0.65,
):
    """
    Pastes a character image onto a background image.
    """
    bg = Image.open(background_path).convert("RGB")
    char = Image.open(character_path).convert("RGBA")

    # Resize character to a percentage of background height
    target_height = int(bg.height * character_scale)
    ratio = target_height / char.height
    new_width = int(char.width * ratio)
    char = char.resize((new_width, target_height), Image.LANCZOS)

    # Position near bottom center
    x = (bg.width - char.width) // 2
    y = int(bg.height * vertical_position) - char.height

    # Paste with alpha if available
    if char.mode == "RGBA":
        bg.paste(char, (x, y), char)
    else:
        bg.paste(char, (x, y))

    if output_dir is None:
        output_dir = SCENES_DIR
    os.makedirs(output_dir, exist_ok=True)

    base = os.path.splitext(os.path.basename(character_path))[0] + "_" + os.path.splitext(os.path.basename(background_path))[0]
    out_path = os.path.join(output_dir, f"composed_{base}.png")
    bg.save(out_path)
    return out_path