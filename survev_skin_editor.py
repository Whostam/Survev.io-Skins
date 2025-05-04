import streamlit as st
from PIL import Image, ImageDraw
import io

st.set_page_config(page_title="Survev.io Skin Editor", layout="centered")
st.title("🎨 Survev.io Skin Editor")
st.write("Customize with solid colors or gradients!")

# --- UI Helpers ---
def gradient_controls(name, default1, default2):
    st.subheader(name)
    typ = st.selectbox(f"{name} fill type", ["Solid", "Linear", "Radial"], key=f"{name}_type")
    c1  = st.color_picker(f"{name} primary color", default1, key=f"{name}_c1")
    c2  = None
    if typ != "Solid":
        c2 = st.color_picker(f"{name} secondary color", default2, key=f"{name}_c2")
    return typ, c1, c2

# --- Collect settings for each part ---
bp_type, bp_c1, bp_c2 = gradient_controls("Backpack", "#A0522D", "#8B4513")
bd_type, bd_c1, bd_c2 = gradient_controls("Body",     "#FFD39F", "#FFC071")
h_type,  h_c1,  h_c2  = gradient_controls("Hands",    "#A0522D", "#8B4513")

# Outline and positioning (as before) …
outline_color = st.color_picker("Outline color", "#000000")
outline_width = st.slider("Outline width", 0, 50, 10)
backpack_offset_y = st.slider("Backpack vertical offset", -300, 300, -150)
hand_offset_x     = st.slider("Hands horizontal offset", 0, 300, 180)
hand_offset_y     = st.slider("Hands vertical offset",   0, 300, 220)

# Optional background upload…
uploaded = st.file_uploader("Upload background skin (PNG)", type=["png"])
bg = None
if uploaded:
    bg = Image.open(uploaded).convert("RGBA").resize((1024,1024), Image.Resampling.LANCZOS)

# --- Gradient generation ---
def make_linear_gradient(size, c1, c2):
    """Top→bottom gradient."""
    base = Image.new("RGB", (1, size), None)
    draw = ImageDraw.Draw(base)
    for y in range(size):
        f = y / (size - 1)
        r = int((1-f)*int(c1[1:3],16) + f*int(c2[1:3],16))
        g = int((1-f)*int(c1[3:5],16) + f*int(c2[3:5],16))
        b = int((1-f)*int(c1[5:7],16) + f*int(c2[5:7],16))
        draw.point((0, y), fill=(r,g,b))
    return base.resize((size, size))

def make_radial_gradient(size, c1, c2):
    """Center-out radial gradient."""
    grad = Image.new("RGB", (size, size), None)
    cx, cy = size//2, size//2
    maxr = (2**0.5)*(size/2)
    draw = ImageDraw.Draw(grad)
    for y in range(size):
        for x in range(size):
            d = ((x-cx)**2 + (y-cy)**2)**0.5 / maxr
            f = min(d, 1.0)
            r = int((1-f)*int(c1[1:3],16) + f*int(c2[1:3],16))
            g = int((1-f)*int(c1[3:5],16) + f*int(c2[3:5],16))
            b = int((1-f)*int(c1[5:7],16) + f*int(c2[5:7],16))
            draw.point((x, y), fill=(r,g,b))
    return grad

def get_fill_image(typ, c1, c2, size):
    if typ == "Solid":
        img = Image.new("RGB", (size, size), c1)
    elif typ == "Linear":
        img = make_linear_gradient(size, c1, c2)
    else:  # Radial
        img = make_radial_gradient(size, c1, c2)
    return img

# --- Draw everything on high-res canvas ---
canvas = Image.new("RGBA", (1024,1024), (0,0,0,0))
draw = ImageDraw.Draw(canvas)

parts = [
    (bp_type, bp_c1, bp_c2, (512, 512+backpack_offset_y), 240),
    (bd_type, bd_c1, bd_c2, (512, 512),               280),
    (h_type,  h_c1,  h_c2,  (512-hand_offset_x, 512+hand_offset_y), 100),
    (h_type,  h_c1,  h_c2,  (512+hand_offset_x, 512+hand_offset_y), 100),
]

for typ, c1, c2, center, radius in parts:
    # generate gradient or solid fill
    fill_img = get_fill_image(typ, c1, c2, 2*radius)
    # mask to circle
    mask = Image.new("L", (2*radius, 2*radius), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.ellipse((0,0,2*radius,2*radius), fill=255)
    # paste onto canvas
    canvas.paste(fill_img, (center[0]-radius, center[1]-radius), mask)

    # draw outline
    oled = ImageDraw.Draw(canvas)
    oled.ellipse(
        (center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius),
        outline=outline_color,
        width=outline_width
    )

# composite background under everything
if bg:
    canvas = Image.alpha_composite(bg, canvas)

# Preview & download
preview = canvas.resize((256,256), Image.Resampling.LANCZOS)
st.subheader("Preview")
st.image(preview)

# Download
out = canvas.resize((512,512), Image.Resampling.LANCZOS)
buf = io.BytesIO()
out.save(buf, format="PNG")
buf.seek(0)
st.download_button("Download Skin", data=buf, file_name="survev_skin.png", mime="image/png")
