import os
import json
import random

# Utility to determine if text should be white or black based on background brightness
def get_foreground_color(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    # Perceived brightness formula
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return '#000000' if brightness > 128 else '#FFFFFF'

# Generate a random hex color
def random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF)).upper()

# Create .vscode directory
vscode_dir = os.path.join(os.getcwd(), '.vscode')
os.makedirs(vscode_dir, exist_ok=True)

# Generate random background color and matching foreground
bg_color = random_color()
fg_color = get_foreground_color(bg_color)

settings = {
    "workbench.colorCustomizations": {
        "statusBar.background": bg_color,
        "statusBar.foreground": fg_color,
        "titleBar.activeBackground": bg_color,
        "titleBar.activeForeground": fg_color,
        "titleBar.inactiveBackground": bg_color,
        "titleBar.inactiveForeground": fg_color
    }
}

# Write to settings.json
settings_path = os.path.join(vscode_dir, 'settings.json')
with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=4)

print(f"settings.json created with background {bg_color} and foreground {fg_color}")
