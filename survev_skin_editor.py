import streamlit as st
from PIL import Image, ImageDraw
import io

st.set_page_config(page_title="Survev.io Skin Editor", layout="wide")
st.title("🎨 Survev.io Skin Editor")
st.write("Use the sidebar to customize gradients, patterns, outlines & positions.")

# --- Gradient helpers (unchanged) ---
def make_linear_gradient(size, c1, c2):
    base = Image.new("RGB", (1, size), None)
    d = ImageDraw.Draw(base)
    for y in range(size):
        f = y / (size - 1)
        r = int((1-f)*int(c1[1:3],16) + f*int(c2[1:3],16))
        g = int((1-f)*int(c1[3:5],16) + f*int(c2[3:5],16))
        b = int((1-f)*int(c1[5:7],16) + f*int(c2[5:7],16))
        d.point((0, y), fill=(r,g,b))
    return base.resize((size, size))

def make_radial_gradient(size, c1, c2):
    grad = Image.new("RGB", (size, size), None)
    cx, cy = size//2, size//2
    maxr = (2**0.5)*(size/2)
    d = ImageDraw.Draw(grad)
    for y in range(size):
        for x in range(size):
            d_norm = ((x-cx)**2 + (y-cy)**2)**0.5 / maxr
            f = min(d_norm, 1.0)
            r = int((1-f)*int(c1[1:3],16) + f*int(c2[1:3],16))
            g = int((1-f)*int(c1[3:5],16) + f*int(c2[3:5],16))
            b = int((1-f)*int(c1[5:7],16) + f*int(c2[5:7],16))
            d.point((x, y), fill=(r,g,b))
    return grad

def get_fill_image(ftype, c1, c2, size):
    if ftype=="Solid":
        return Image.new("RGB", (size, size), c1)
    if ftype=="Linear":
        return make_linear_gradient(size, c1, c2)
    return make_radial_gradient(size, c1, c2)

# --- Pattern generators ---
def make_stripes(size, bg, fg, stripe_w=20):
    tile = Image.new("RGBA", (size, size), bg)
    d = ImageDraw.Draw(tile)
    for x in range(0, size, stripe_w*2):
        d.rectangle([x, 0, x+stripe_w, size], fill=fg)
    return tile

def make_spots(size, bg, fg, dot_r=30, spacing=60):
    tile = Image.new("RGBA", (size, size), bg)
    d = ImageDraw.Draw(tile)
    for y in range(0, size, spacing):
        for x in range(0, size, spacing):
            d.ellipse((x, y, x+dot_r, y+dot_r), fill=fg)
    return tile

def make_diagonal_stripes(size, bg, fg, stripe_w=20):
    tile = Image.new("RGBA", (size, size), bg)
    d = ImageDraw.Draw(tile)
    # draw lines from left-bottom to right-top
    for x in range(-size, size, stripe_w*2):
        d.line([(x, size), (x+size, 0)], fill=fg, width=stripe_w)
    return tile

def make_checkerboard(size, c1, c2, block=50):
    tile = Image.new("RGBA", (size, size), c1)
    d = ImageDraw.Draw(tile)
    for y in range(0, size, block):
        for x in range(0, size, block):
            if ((x//block)+(y//block)) % 2 == 0:
                d.rectangle([x, y, x+block, y+block], fill=c2)
    return tile

# --- Sidebar controls ---
with st.sidebar:
    def part_ui(name, default1, default2):
        st.header(name)
        ftype = st.selectbox("Fill type", ["Solid","Linear","Radial"], key=f"{name}_fill")
        c1 = st.color_picker("Primary color", default1, key=f"{name}_c1")
        c2 = c1
        if ftype!="Solid":
            c2 = st.color_picker("Secondary color", default2, key=f"{name}_c2")

        # only allow patterns if not solid
        patterns = ["None"] if ftype=="Solid" else ["None","Stripes","Spots","Diagonal Stripes","Checkerboard","Custom"]
        pat = st.selectbox("Pattern", patterns, key=f"{name}_pat")
        pat_c1 = pat_c2 = None
        if pat!="None" and pat!="Custom":
            pat_c1 = st.color_picker("Pattern color 1", default1, key=f"{name}_pc1")
            pat_c2 = st.color_picker("Pattern color 2", default2, key=f"{name}_pc2")
        custom = None
        if pat=="Custom":
            custom = st.file_uploader("Upload tile PNG", type="png", key=f"{name}_up")
        return ftype, c1, c2, pat, pat_c1, pat_c2, custom

    bp_fill, bp_c1, bp_c2, bp_pat, bp_pc1, bp_pc2, bp_up = part_ui("Backpack", "#A0522D", "#8B4513")
    st.markdown("---")
    bd_fill, bd_c1, bd_c2, bd_pat, bd_pc1, bd_pc2, bd_up = part_ui("Body",     "#FFD39F", "#FFC071")
    st.markdown("---")
    h_fill,  h_c1,  h_c2,  h_pat,  h_pc1,  h_pc2,  h_up  = part_ui("Hands",    "#A0522D", "#8B4513")
    st.markdown("---")
    st.header("Outline & Position")
    outline_color     = st.color_picker("Outline color", "#000000")
    outline_width     = st.slider("Outline width", 0, 50, 10)
    backpack_offset_y = st.slider("Backpack Y offset", -300, 300, -150)
    hand_offset_x     = st.slider("Hands X offset",      0, 300, 180)
    hand_offset_y     = st.slider("Hands Y offset",      0, 300, 220)
    st.markdown("---")
    bg_file = st.file_uploader("Optional background (PNG)", type="png")

# --- Load background ---
bg = None
if bg_file:
    bg = Image.open(bg_file).convert("RGBA").resize((1024,1024), Image.Resampling.LANCZOS)

# --- Build canvas ---
canvas = Image.new("RGBA", (1024,1024), (0,0,0,0))
parts = [
    (bp_fill, bp_c1, bp_c2, bp_pat, bp_pc1, bp_pc2, bp_up, (512,512+backpack_offset_y), 240),
    (bd_fill, bd_c1, bd_c2, bd_pat, bd_pc1, bd_pc2, bd_up, (512,512),               280),
    (h_fill,  h_c1,  h_c2,  h_pat,  h_pc1,  h_pc2,  h_up,  (512-hand_offset_x,512+hand_offset_y), 100),
    (h_fill,  h_c1,  h_c2,  h_pat,  h_pc1,  h_pc2,  h_up,  (512+hand_offset_x,512+hand_offset_y), 100),
]

for ftype, c1, c2, pat, pc1, pc2, up, center, r in parts:
    # 1) base fill
    fill_img = get_fill_image(ftype, c1, c2, 2*r)

    # 2) pattern overlay
    pattern_img = None
    if pat=="Stripes":
        pattern_img = make_stripes(2*r, pc1, pc2)
    elif pat=="Spots":
        pattern_img = make_spots(2*r, pc1, pc2)
    elif pat=="Diagonal Stripes":
        pattern_img = make_diagonal_stripes(2*r, pc1, pc2)
    elif pat=="Checkerboard":
        pattern_img = make_checkerboard(2*r, pc1, pc2)
    elif pat=="Custom" and up:
        pattern_img = Image.open(up).convert("RGBA") \
                           .resize((2*r,2*r), Image.Resampling.LANCZOS)
    elif pat=="Custom":
        st.warning(f"{center}: no custom tile uploaded; skipping pattern.")

    if pattern_img:
        mask = Image.new("L", (2*r,2*r), 0)
        ImageDraw.Draw(mask).ellipse((0,0,2*r,2*r), fill=255)
        fill_img = Image.composite(pattern_img, fill_img, mask)

    # 3) always build the circle mask
    mask = Image.new("L", (2*r,2*r), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.ellipse((0,0,2*r,2*r), fill=255)

    # 4) paste
    canvas.paste(fill_img, (center[0]-r, center[1]-r), mask)

    # 5) outline
    ImageDraw.Draw(canvas).ellipse(
        (center[0]-r, center[1]-r, center[0]+r, center[1]+r),
        outline=outline_color, width=outline_width
    )

# 6) composite background
if bg:
    canvas = Image.alpha_composite(bg, canvas)

# --- Preview & Download ---
preview = canvas.resize((256,256), Image.Resampling.LANCZOS)
st.subheader("Preview")
st.image(preview)

download = canvas.resize((512,512), Image.Resampling.LANCZOS)
buf = io.BytesIO()
download.save(buf, format="PNG")
buf.seek(0)

st.download_button("Download Skin", data=buf, file_name="survev_skin.png", mime="image/png")
