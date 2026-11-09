#!/usr/bin/env python3
"""Generate the Terminal app icon set (macOS + Pillow)."""

import json
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(ROOT, "icon-master.png")
ASSETS = os.path.join(ROOT, "Assets.xcassets")
ICONSET = os.path.join(ASSETS, "DisplayIcon.appiconset")
OUT = os.path.join(ROOT, "out")

SIZE = 1024

# Background gradient (deep blue-black to black).
img = Image.new("RGB", (SIZE, SIZE), (5, 7, 10))
pix = img.load()
for y in range(SIZE):
    t = y / (SIZE - 1)
    r = int(8 + 10 * t)
    g = int(13 + 15 * t)
    b = int(20 + 22 * t)
    for x in range(SIZE):
        # A very subtle vertical/horizontal vignette.
        edge = min(x, SIZE - 1 - x, y, SIZE - 1 - y) / (SIZE / 2)
        v = 0.85 + 0.15 * min(1.0, edge)
        pix[x, y] = (int(r * v), int(g * v), int(b * v))

draw = ImageDraw.Draw(img)

# Terminal card.
card = (112, 154, 912, 870)
radius = 96
draw.rounded_rectangle(card, radius=radius, fill=(13, 17, 23), outline=(48, 54, 61), width=10)

# Top bar with traffic-light dots.
top = (112, 154, 912, 300)
draw.rounded_rectangle(top, radius=radius, fill=(22, 27, 34))
draw.rectangle((112, 250, 912, 300), fill=(22, 27, 34))
draw.line((112, 300, 912, 300), fill=(48, 54, 61), width=6)
for cx, color in ((206, (255, 95, 86)), (286, (255, 189, 46)), (366, (39, 201, 63))):
    draw.ellipse((cx - 28, 201, cx + 28, 257), fill=color)

# Green prompt glow.
glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
gdraw = ImageDraw.Draw(glow)
try:
    font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 400, index=1)
except Exception:
    font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 400, index=0)
text = ">_"
bbox = gdraw.textbbox((0, 0), text, font=font)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
tx = (SIZE - tw) // 2 - bbox[0]
ty = 430 - bbox[1]
gdraw.text((tx, ty), text, font=font, fill=(57, 211, 83, 255))
glow = glow.filter(ImageFilter.GaussianBlur(34))
img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
draw = ImageDraw.Draw(img)

# Crisp prompt and a terminal cursor block.
draw.text((tx, ty), text, font=font, fill=(63, 185, 80))
cursor_x = tx + tw + 28
cursor_y = ty + int(th * 0.58)
draw.rounded_rectangle((cursor_x, cursor_y, cursor_x + 92, cursor_y + 30), radius=8, fill=(63, 185, 80))

# A faint bottom label.
try:
    label_font = ImageFont.truetype("/System/Library/Fonts/SFNSMono.ttf", 44)
except Exception:
    label_font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 54)
label = "Terminal"
lbbox = draw.textbbox((0, 0), label, font=label_font)
lw = lbbox[2] - lbbox[0]
draw.text(((SIZE - lw) // 2, 780), label, font=label_font, fill=(88, 166, 255))

img.save(MASTER)

# Asset catalog.
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT, exist_ok=True)
if os.path.isdir(ASSETS):
    shutil.rmtree(ASSETS)
os.makedirs(ICONSET, exist_ok=True)
with open(os.path.join(ASSETS, "Contents.json"), "w") as f:
    json.dump({"info": {"author": "xcode", "version": 1}}, f, indent=2)

# (idiom, size, scale, filename)
specs = [
    ("iphone", "20x20", "2x", "DisplayIcon20x20@2x.png"),
    ("iphone", "20x20", "3x", "DisplayIcon20x20@3x.png"),
    ("iphone", "29x29", "2x", "DisplayIcon29x29@2x.png"),
    ("iphone", "29x29", "3x", "DisplayIcon29x29@3x.png"),
    ("iphone", "40x40", "2x", "DisplayIcon40x40@2x.png"),
    ("iphone", "40x40", "3x", "DisplayIcon40x40@3x.png"),
    ("iphone", "60x60", "2x", "DisplayIcon60x60@2x.png"),
    ("iphone", "60x60", "3x", "DisplayIcon60x60@3x.png"),
    ("ipad", "20x20", "1x", "DisplayIcon20x20~ipad.png"),
    ("ipad", "20x20", "2x", "DisplayIcon20x20@2x~ipad.png"),
    ("ipad", "29x29", "1x", "DisplayIcon29x29~ipad.png"),
    ("ipad", "29x29", "2x", "DisplayIcon29x29@2x~ipad.png"),
    ("ipad", "40x40", "1x", "DisplayIcon40x40~ipad.png"),
    ("ipad", "40x40", "2x", "DisplayIcon40x40@2x~ipad.png"),
    ("ipad", "76x76", "1x", "DisplayIcon76x76~ipad.png"),
    ("ipad", "76x76", "2x", "DisplayIcon76x76@2x~ipad.png"),
    ("ipad", "83.5x83.5", "2x", "DisplayIcon83.5x83.5@2x~ipad.png"),
    ("ios-marketing", "1024x1024", "1x", "DisplayIcon1024.png"),
]
images = []
for idiom, size, scale, name in specs:
    points = float(size.split("x")[0])
    px = int(round(points * int(scale.rstrip("x"))))
    resized = img.resize((px, px), Image.LANCZOS)
    resized.save(os.path.join(ICONSET, name))
    images.append({"filename": name, "idiom": idiom, "scale": scale, "size": size})
with open(os.path.join(ICONSET, "Contents.json"), "w") as f:
    json.dump({"images": images, "info": {"author": "xcode", "version": 1}}, f, indent=2)

# Compile the asset catalog with Xcode's actool.
subprocess.run([
    "xcrun", "actool",
    "--compile", OUT,
    "--platform", "iphoneos",
    "--minimum-deployment-target", "15.0",
    "--app-icon", "DisplayIcon",
    "--output-partial-info-plist", os.path.join(OUT, "partial-info.plist"),
    "--target-device", "iphone",
    "--target-device", "ipad",
    ASSETS,
], check=True)

print("master:", MASTER)
print("assets.car:", os.path.join(OUT, "Assets.car"))
print("generated files:")
for name in sorted(os.listdir(OUT)):
    print(" ", name)
