import streamlit as st
from PIL import Image, ImageDraw
import io

st.set_page_config(page_title="Survev.io Skin Editor", layout="wide")
st.title("🎨 Survev.io Skin Editor")
st.write("Use the sidebar to customize gradients, patterns, outlines & positions.")

# --- Helper functions for gradients ---
def make_linear_gradient(size, c1, c2):
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

def get_fill_image(fill_type, c1, c2, size):
    if fill_type == "Solid":
        return Image.new("RGB", (size, size), c1)
    if fill_type == "Linear":
        return make_linear_gradient(size, c1, c2)
    return make_radial_gradient(size, c1, c2)

# --- Pattern generators ---
def make_stripes(size, c_bg, c_fg, stripe_width=20):
    tile = Image.new("RGBA", (size, size), c_bg)
    draw = ImageDraw.Draw(tile)
    for x in range(0, size, stripe_width*2):
        draw.rectangle([x, 0, x+stripe_width, size], fill=c_fg)
    return tile

def make_spots(size, c_bg, c_fg, dot_radius=30, spacing=60):
    tile = Image.new("RGBA", (size, size), c_bg)
    draw = ImageDraw.Draw(tile)
    for y in range(0, size, spacing):
        for x in range(0, size, spacing):
            draw.ellipse((x, y, x+dot_radius, y+dot_radius), fill=c_fg)
    return tile

# --- Sidebar for controls ---
with st.sidebar:
    st.header("Backpack")
    bp_fill = st.selectbox("Fill type", ["Solid","Linear","Radial"], key="bp_fill")
    bp_c1 = st.color_picker("Primary color", "#A0522D", key="bp_c1")
    bp_c2 = st.color_picker("Secondary color", "#8B4513", key="bp_c2") if bp_fill!="Solid" else bp_c1
    bp_pattern = st.selectbox("Pattern", ["None","Stripes","Spots","Custom"], key="bp_pattern")
    bp_custom = st.file_uploader("Upload tile PNG", type="png", key="bp_patup") if bp_pattern=="Custom" else None

    st.markdown("---")
    st.header("Body")
    bd_fill = st.selectbox("Fill type", ["Solid","Linear","Radial"], key="bd_fill")
    bd_c1 = st.color_picker("Primary color", "#FFD39F", key="bd_c1")
    bd_c2 = st.color_picker("Secondary color", "#FFC071", key="bd_c2") if bd_fill!="Solid" else bd_c1
    bd_pattern = st.selectbox("Pattern", ["None","Stripes","Spots","Custom"], key="bd_pattern")
    bd_custom = st.file_uploader("Upload tile PNG", type="png", key="bd_patup") if bd_pattern=="Custom" else None

    st.markdown("---")
    st.header("Hands")
    h_fill = st.selectbox("Fill type", ["Solid","Linear","Radial"], key="h_fill")
    h_c1 = st.color_picker("Primary color", "#A0522D", key="h_c1")
    h_c2 = st.color_picker("Secondary color", "#8B4513", key="h_c2") if h_fill!="Solid" else h_c1
    h_pattern = st.selectbox("Pattern", ["None","Stripes","Spots","Custom"], key="h_pattern")
    h_custom = st.file_uploader("Upload tile PNG", type="png", key="h_patup") if h_pattern=="Custom" else None

    st.markdown("---")
    st.header("Outline & Position")
    outline_color     = st.color_picker("Outline color", "#000000")
    outline_width     = st.slider("Outline width", 0, 50, 10)
    backpack_offset_y = st.slider("Backpack Y offset", -300, 300, -150)
    hand_offset_x     = st.slider("Hands X offset", 0, 300, 180)
    hand_offset_y     = st.slider("Hands Y offset", 0, 300, 220)

    st.markdown("---")
    uploaded_file = st.file_uploader("Optional background (PNG)", type=["png"])

# --- Optional background layer ---
bg = None
if uploaded_file:
    bg = Image.open(uploaded_file).convert("RGBA").resize((1024,1024), Image.Resampling.LANCZOS)

# --- Build the 1024×1024 canvas ---
canvas = Image.new("RGBA", (1024,1024), (0,0,0,0))

parts = [
    (bp_fill, bp_c1, bp_c2, bp_pattern, bp_custom, (512,512+backpack_offset_y), 240),
    (bd_fill, bd_c1, bd_c2, bd_pattern, bd_custom, (512,512),               280),
    (h_fill,  h_c1,  h_c2,  h_pattern,  h_custom,  (512-hand_offset_x,512+hand_offset_y), 100),
    (h_fill,  h_c1,  h_c2,  h_pattern,  h_custom,  (512+hand_offset_x,512+hand_offset_y), 100),
]

for fill_type, c1, c2, pat, custom, center, r in parts:
    # 1) Base fill (solid or gradient)
    fill_img = get_fill_image(fill_type, c1, c2, 2*r)

    # 2) Pattern overlay, only if we have a valid pattern image
    pattern_img = None
    if pat == "Stripes":
        pattern_img = make_stripes(2*r, c1, c2)
    elif pat == "Spots":
        pattern_img = make_spots(2*r, c1, c2)
    elif pat == "Custom":
        if custom:
            pattern_img = Image.open(custom).convert("RGBA") \
                          .resize((2*r,2*r), Image.Resampling.LANCZOS)
        else:
            st.warning("Custom pattern selected but no file uploaded; skipping that overlay.")

    if pattern_img:
        mask = Image.new("L", (2*r,2*r), 0)
        ImageDraw.Draw(mask).ellipse((0,0,2*r,2*r), fill=255)
        fill_img = Image.composite(pattern_img, fill_img, mask)

    # 3) Always build the circular mask for pasting
    mask = Image.new("L", (2*r, 2*r), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.ellipse((0, 0, 2*r, 2*r), fill=255)

    # 4) Paste into the canvas
    canvas.paste(fill_img, (center[0]-r, center[1]-r), mask)

    # 5) Draw outline
    ImageDraw.Draw(canvas).ellipse(
        (center[0]-r, center[1]-r, center[0]+r, center[1]+r),
        outline=outline_color, width=outline_width
    )

# 6) Composite the optional background underneath
if bg:
    canvas = Image.alpha_composite(bg, canvas)

# --- Preview & Download ---
preview = canvas.resize((256,256), Image.Resampling.LANCZOS)
st.subheader("Preview")
st.image(preview)

download_img = canvas.resize((512,512), Image.Resampling.LANCZOS)
buf = io.BytesIO()
download_img.save(buf, format="PNG")
buf.seek(0)

st.download_button(
    "Download Skin",
    data=buf,
    file_name="survev_skin.png",
    mime="image/png"
)
