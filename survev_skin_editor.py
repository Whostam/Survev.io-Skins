import streamlit as st
from PIL import Image, ImageDraw

st.set_page_config(page_title="Survev.io Skin Editor", layout="centered")

st.title("🎨 Survev.io Skin Editor")
st.write("Customize your own skin using the layout: Backpack → Body → Hands")

# --- Color selectors ---
backpack_color = st.color_picker("Backpack color", "#A0522D")
body_color = st.color_picker("Body color", "#FFD39F")
hands_color = st.color_picker("Hands color", "#A0522D")

# Create canvas
canvas_size = 256
img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# --- Sizes and positions ---
center = canvas_size // 2
body_radius = 70
backpack_radius = 60
hand_radius = 25

# --- Coordinates ---
# Backpack (behind body, slightly above)
backpack_center = (center, center - 30)
# Body (center)
body_center = (center, center)
# Hands (bottom left & right of body)
hand_offset_y = 50
hand_offset_x = 40
left_hand_center = (center - hand_offset_x, center + hand_offset_y)
right_hand_center = (center + hand_offset_x, center + hand_offset_y)

def draw_circle(center, radius, color):
    x, y = center
    return draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)

# --- Draw the parts in correct layer order ---
draw_circle(backpack_center, backpack_radius, backpack_color)  # Backpack (bottom layer)
draw_circle(body_center, body_radius, body_color)              # Body (middle layer)
draw_circle(left_hand_center, hand_radius, hands_color)        # Hands (top layer)
draw_circle(right_hand_center, hand_radius, hands_color)

# --- Show preview ---
st.subheader("Skin Preview")
st.image(img, use_column_width=True)

# --- Download button ---
img_download = img.convert("RGB")
st.download_button("Download Skin", data=img_download.tobytes(), file_name="survev_skin.png", mime="image/png")
