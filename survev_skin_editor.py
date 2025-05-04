import streamlit as st
from PIL import Image, ImageDraw, ImageOps

st.set_page_config(page_title="Survev.io Skin Editor", layout="centered")
st.title("🎨 Survev.io Skin Editor")
st.write("Customize your own Survev.io-style skin!")

# --- Color selectors ---
backpack_color = st.color_picker("Backpack color", "#A0522D")
body_color = st.color_picker("Body color", "#FFD39F")
hands_color = st.color_picker("Hands color", "#A0522D")

# --- Upload base image (optional) ---
uploaded_file = st.file_uploader("Optional: Upload a background skin (PNG)", type=["png"])
background_img = None
if uploaded_file:
    background_img = Image.open(uploaded_file).convert("RGBA").resize((1024, 1024))

# --- Create canvas ---
canvas_size = 1024  # High-res for smooth shapes
img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# --- Sizes and positions (scaled for 1024x1024) ---
center = canvas_size // 2
body_radius = 280
backpack_radius = 240
hand_radius = 100

# Coordinates
backpack_center = (center, center - 120)
body_center = (center, center)
hand_offset_y = 200
hand_offset_x = 160
left_hand_center = (center - hand_offset_x, center + hand_offset_y)
right_hand_center = (center + hand_offset_x, center + hand_offset_y)

def draw_circle(center, radius, color):
    x, y = center
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)

# --- Draw layers ---
if background_img:
    img = Image.alpha_composite(background_img, img)

draw = ImageDraw.Draw(img)
draw_circle(backpack_center, backpack_radius, backpack_color)
draw_circle(body_center, body_radius, body_color)
draw_circle(left_hand_center, hand_radius, hands_color)
draw_circle(right_hand_center, hand_radius, hands_color)

# --- Resize to display size ---
display_img = img.resize((256, 256), Image.Resampling.LANCZOS)

# --- Show result ---
st.subheader("Skin Preview")
st.image(display_img)

import io

# --- Prepare valid PNG in memory ---
buffer = io.BytesIO()
download_img.save(buffer, format="PNG")
buffer.seek(0)

# --- Download button with valid PNG ---
st.download_button(
    "Download Skin",
    data=buffer,
    file_name="survev_skin.png",
    mime="image/png"
)
