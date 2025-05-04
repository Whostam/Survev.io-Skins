import streamlit as st
from PIL import Image, ImageDraw
import io

st.set_page_config(page_title="Survev.io Skin Editor", layout="wide")
st.title("🎨 Survev.io Skin Editor")
st.write("Use the sidebar to customize gradients, patterns, outlines & positions.")

# ─── Gradient helpers ──────────────────────────────────────────────────────
def make_linear_gradient(size, c1, c2):
    base = Image.new("RGB", (1, size))
    draw = ImageDraw.Draw(base)
    for y in range(size):
        t = y / (size - 1)
        r = int((1-t)*int(c1[1:3],16) + t*int(c2[1:3],16))
        g = int((1-t)*int(c1[3:5],16) + t*int(c2[3:5],16))
        b = int((1-t)*int(c1[5:7],16) + t*int(c2[5:7],16))
        draw.point((0,y), fill=(r,g,b))
    return base.resize((size, size))

def make_radial_gradient(size, c1, c2):
    grad = Image.new("RGB", (size, size))
    draw = ImageDraw.Draw(grad)
    cx, cy = size//2, size//2
    maxr = (2**0.5)*(size/2)
    for y in range(size):
        for x in range(size):
            d = ((x-cx)**2 + (y-cy)**2)**0.5 / maxr
            t = min(d,1.0)
            r = int((1-t)*int(c1[1:3],16) + t*int(c2[1:3],16))
            g = int((1-t)*int(c1[3:5],16) + t*int(c2[3:5],16))
            b = int((1-t)*int(c1[5:7],16) + t*int(c2[5:7],16))
            draw.point((x,y), fill=(r,g,b))
    return grad

def get_fill_image(ftype, c1, c2, size):
    if ftype == "Solid":
        return Image.new("RGB", (size, size), c1)
    if ftype == "Linear":
        return make_linear_gradient(size, c1, c2)
    return make_radial_gradient(size, c1, c2)

# ─── Pattern generators (transparent bg) ─────────────────────────────────
def make_stripes(size, color, stripe_w=20):
    tile = Image.new("RGBA", (size,size), (0,0,0,0))
    draw = ImageDraw.Draw(tile)
    for x in range(0, size, stripe_w*2):
        draw.rectangle([x, 0, x+stripe_w, size], fill=color)
    return tile

def make_spots(size, color, dot_r=30, spacing=60):
    tile = Image.new("RGBA", (size,size), (0,0,0,0))
    draw = ImageDraw.Draw(tile)
    for y in range(0, size, spacing):
        for x in range(0, size, spacing):
            draw.ellipse([x, y, x+dot_r, y+dot_r], fill=color)
    return tile

def make_diagonal_stripes(size, color, stripe_w=20):
    tile = Image.new("RGBA", (size,size), (0,0,0,0))
    draw = ImageDraw.Draw(tile)
    for x in range(-size, size, stripe_w*2):
        draw.line([(x, size), (x+size, 0)], fill=color, width=stripe_w)
    return tile

def make_checkerboard(size, color, block=50):
    tile = Image.new("RGBA", (size,size), (0,0,0,0))
    draw = ImageDraw.Draw(tile)
    for y in range(0, size, block):
        for x in range(0, size, block):
            if ((x//block)+(y//block)) % 2 == 0:
                draw.rectangle([x,y,x+block,y+block], fill=color)
    return tile

# ─── Sidebar UI ───────────────────────────────────────────────────────────
with st.sidebar:
    def part_ui(name, def1, def2):
        st.header(name)
        ftype = st.selectbox("Fill type", ["Solid","Linear","Radial"], key=f"{name}_fill")
        c1 = st.color_picker("Primary color", def1, key=f"{name}_c1")
        c2 = c1
        if ftype != "Solid":
            c2 = st.color_picker("Secondary color", def2, key=f"{name}_c2")

        pat = st.selectbox(
            "Pattern",
            ["None","Stripes","Spots","Diagonal Stripes","Checkerboard","Custom"],
            key=f"{name}_pat"
        )
        pat_color = None
        pat_file  = None
        if pat != "None":
            if pat != "Custom":
                pat_color = st.color_picker("Pattern color", def2, key=f"{name}_pc")
            else:
                pat_file = st.file_uploader("Upload tile PNG", type="png", key=f"{name}_up")
        return ftype, c1, c2, pat, pat_color, pat_file

    bp_fill, bp_c1, bp_c2, bp_pat, bp_pc, bp_up = part_ui("Backpack", "#A0522D", "#8B4513")
    st.markdown("---")
    bd_fill, bd_c1, bd_c2, bd_pat, bd_pc, bd_up = part_ui("Body",     "#FFD39F", "#FFC071")
    st.markdown("---")
    h_fill,  h_c1,  h_c2,  h_pat,  h_pc,  h_up  = part_ui("Hands",    "#A0522D", "#8B4513")
    st.markdown("---")
    st.header("Outline & Position")
    outline_color     = st.color_picker("Outline color", "#000000")
    outline_width     = st.slider("Outline width", 0, 50, 10)
    backpack_offset_y = st.slider("Backpack Y offset", -300, 300, -150)
    hand_offset_x     = st.slider("Hands X offset",      0, 300, 180)
    hand_offset_y     = st.slider("Hands Y offset",      0, 300, 220)
    st.markdown("---")
    bg_file = st.file_uploader("Optional background (PNG)", type="png")

# ─── Load background ────────────────────────────────────────────────────────
bg = None
if bg_file:
    bg = Image.open(bg_file).convert("RGBA") \
             .resize((1024,1024), Image.Resampling.LANCZOS)

# ─── Build 1024×1024 canvas ─────────────────────────────────────────────────
canvas = Image.new("RGBA", (1024,1024), (0,0,0,0))
parts = [
    (bp_fill, bp_c1, bp_c2, bp_pat, bp_pc, bp_up, (512,512+backpack_offset_y), 240),
    (bd_fill, bd_c1, bd_c2, bd_pat, bd_pc, bd_up, (512,512),               280),
    (h_fill,  h_c1,  h_c2,  h_pat,  h_pc,  h_up,  (512-hand_offset_x,512+hand_offset_y), 100),
    (h_fill,  h_c1,  h_c2,  h_pat,  h_pc,  h_up,  (512+hand_offset_x,512+hand_offset_y), 100),
]

for ftype, c1, c2, pat, pc, up, center, r in parts:
    # 1) base fill
    fill_img = get_fill_image(ftype, c1, c2, 2*r)

    # 2) pattern overlay
    pattern = None
    if pat == "Stripes":
        pattern = make_stripes(2*r, pc)
    elif pat == "Spots":
        pattern = make_spots(2*r, pc)
    elif pat == "Diagonal Stripes":
        pattern = make_diagonal_stripes(2*r, pc)
    elif pat == "Checkerboard":
        pattern = make_checkerboard(2*r, pc)
    elif pat == "Custom" and up:
        pattern = Image.open(up).convert("RGBA") \
                       .resize((2*r,2*r), Image.Resampling.LANCZOS)
    elif pat == "Custom":
        st.warning(f"{name} custom pattern: no file uploaded, skipping.")

    if pattern:
        # mask to circle and composite
        mask = Image.new("L", (2*r,2*r), 0)
        ImageDraw.Draw(mask).ellipse((0,0,2*r,2*r), fill=255)
        fill_img = Image.composite(pattern, fill_img, mask)

    # 3) circle mask (always)
    mask = Image.new("L", (2*r,2*r), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0,0,2*r,2*r), fill=255)

    # 4) paste
    canvas.paste(fill_img, (center[0]-r, center[1]-r), mask)

    # 5) outline
    ImageDraw.Draw(canvas).ellipse(
        (center[0]-r, center[1]-r, center[0]+r, center[1]+r),
        outline=outline_color, width=outline_width
    )

# 6) composite background under
if bg:
    canvas = Image.alpha_composite(bg, canvas)

# ─── Preview & Download ────────────────────────────────────────────────────
preview = canvas.resize((256,256), Image.Resampling.LANCZOS)
st.subheader("Preview")
st.image(preview)

out = canvas.resize((512,512), Image.Resampling.LANCZOS)
buf = io.BytesIO()
out.save(buf, format="PNG")
buf.seek(0)
st.download_button("Download Skin", data=buf, file_name="survev_skin.png", mime="image/png")
