import streamlit as st
from PIL import Image, ImageDraw

st.set_page_config(page_title="Survev.io Skin Editor", layout="centered")

st.title("🎨 Survev.io Skin Editor")
st.write("Customize your own Survev.io skin!")

# --- Color selectors ---
body_color = st.color_picker("Choose body color", "#F5D0A0")
pattern_color = st.color_picker("Choose pattern color", "#A05200")
eye_color = st.color_picker("Choose eye color", "#000000")

# --- Load empty base skin (placeholder) ---
base_img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
draw = ImageDraw.Draw(base_img)

# --- Draw skin components (simplified placeholder) ---
# Body
draw.ellipse((56, 56, 200, 200), fill=body_color)

# Pattern (simulate a central patch)
draw.polygon([(128, 90), (140, 110), (130, 140), (110, 130), (105, 110)], fill=pattern_color)

# Eyes
draw.ellipse((85, 155, 105, 175), fill=eye_color)
draw.ellipse((150, 155, 170, 175), fill=eye_color)

# --- Show preview ---
st.subheader("Skin Preview")
st.image(base_img, use_column_width=True)

# --- Download button ---
img_download = base_img.convert("RGB")
st.download_button("Download Skin", data=img_download.tobytes(), file_name="custom_skin.png", mime="image/png")
