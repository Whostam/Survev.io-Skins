import streamlit as st
from PIL import Image, ImageDraw, ImageOps
import io

st.set_page_config(page_title="Survev.io Skin Editor", layout="centered")
st.title("🎨 Survev.io Skin Editor")
st.write("Customize your Survev.io-style skin!")

# --- Color selectors ---
backpack_color = st.color_picker("Backpack color", "#A0522D")
body_color     = st.color_picker("Body color",     "#FFD39F")
hands_color    = st.color_picker("Hands color",    "#A0522D")

# --- Outline options ---
st.subheader("Outline")
outline_color = st.color_picker("Outline color", "#000000")
outline_width = st.slider("Outline width", 0, 50, 10)

# --- Position adjustments ---
st.subheader("Position tweaks")
backpack_offset_y = st.slider("Backpack vertical offset", -300, 300, -150)
hand_offset_x     = st.slider("Hands horizontal offset", 0, 300, 180)
hand_offset_y     = st.slider("Hands vertical offset",   0, 300, 220)

# --- Upload base image (optional) ---
uploaded_file = st.file_uploader("Optional: Upload a background skin (PNG)", type=["png"])
if uploaded_file:
    background_img = (Image.open(uploaded_file)
                          .convert("RGBA")
                          .resize((1024, 1024), Image.Resampling.LANCZOS))
else:
    background_img = None

# --- Create high-res canvas ---
canvas_size = 1024
img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# --- Compute centers & radii ---
center = canvas_size // 2
body_radius     = 280
backpack_radius = 240
hand_radius     = 100

backpack_center = (center, center + backpack_offset_y)
body_center     = (center, center)
left_hand_center  = (center - hand_offset_x, center + hand_offset_y)
right_hand_center = (center + hand_offset_x, center + hand_offset_y)

def draw_circle(c, r, fill, outline, width):
    x, y = c
    bbox = (x-r, y-r, x+r, y+r)
    # Pillow >= 8.2 supports 'width' arg on ellipse
    draw.ellipse(bbox, fill=fill, outline=outline, width=width)

# --- Composite background if any ---
if background_img:
    img = Image.alpha_composite(background_img, img)
    draw = ImageDraw.Draw(img)

# --- Draw layers in order ---
draw_circle(backpack_center, backpack_radius, backpack_color, outline_color, outline_width)
draw_circle(body_center,       body_radius,       body_color,       outline_color, outline_width)
draw_circle(left_hand_center,  hand_radius,       hands_color,      outline_color, outline_width)
draw_circle(right_hand_center, hand_radius,       hands_color,      outline_color, outline_width)

# --- Down‐sample for preview ---
display_img = img.resize((256, 256), Image.Resampling.LANCZOS)
st.subheader("Skin Preview")
st.image(display_img)

# --- Download as a real PNG ---
download_img = img.resize((512, 512), Image.Resampling.LANCZOS)
buffer = io.BytesIO()
download_img.save(buffer, format="PNG")
buffer.seek(0)

st.download_button(
    "Download Skin",
    data=buffer,
    file_name="survev_skin.png",
    mime="image/png"
)
