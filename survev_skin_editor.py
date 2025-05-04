import streamlit as st
import json, random, io, base64
from PIL import Image, ImageDraw

st.set_page_config(page_title="Survev.io Skin Editor", layout="wide")
st.title("🎨 Survev.io Skin Editor")
st.write("Use the sidebar (or the 🎲 Randomize button) to customize or auto-generate a skin.")

# ─── Helper Functions ────────────────────────────────────────────────────────

def make_linear_gradient(size, c1, c2):
    img = Image.new("RGB", (1, size))
    d = ImageDraw.Draw(img)
    for y in range(size):
        t = y/(size-1)
        r = int((1-t)*int(c1[1:3],16) + t*int(c2[1:3],16))
        g = int((1-t)*int(c1[3:5],16) + t*int(c2[3:5],16))
        b = int((1-t)*int(c1[5:7],16) + t*int(c2[5:7],16))
        d.point((0,y), fill=(r,g,b))
    return img.resize((size, size))

def make_radial_gradient(size, c1, c2):
    img = Image.new("RGB", (size, size))
    d = ImageDraw.Draw(img)
    cx = cy = size//2
    maxr = (2**0.5)*(size/2)
    for y in range(size):
        for x in range(size):
            d_norm = ((x-cx)**2 + (y-cy)**2)**0.5 / maxr
            t = min(d_norm, 1.0)
            r = int((1-t)*int(c1[1:3],16) + t*int(c2[1:3],16))
            g = int((1-t)*int(c1[3:5],16) + t*int(c2[3:5],16))
            b = int((1-t)*int(c1[5:7],16) + t*int(c2[5:7],16))
            d.point((x,y), fill=(r,g,b))
    return img

def get_fill_image(ftype, c1, c2, size):
    if ftype=="Solid":
        return Image.new("RGB", (size,size), c1)
    if ftype=="Linear":
        return make_linear_gradient(size, c1, c2)
    return make_radial_gradient(size, c1, c2)

def make_stripes(size, color, stripe_w):
    pat = Image.new("RGBA", (size,size), (0,0,0,0))
    d = ImageDraw.Draw(pat)
    for x in range(0, size, stripe_w*2):
        d.rectangle([x,0,x+stripe_w,size], fill=color)
    return pat

def make_spots(size, color, dot_r, spacing):
    pat = Image.new("RGBA", (size,size), (0,0,0,0))
    d = ImageDraw.Draw(pat)
    for y in range(0, size, spacing):
        for x in range(0, size, spacing):
            d.ellipse([x,y,x+dot_r,y+dot_r], fill=color)
    return pat

def make_diagonal_stripes(size, color, stripe_w):
    pat = Image.new("RGBA", (size,size), (0,0,0,0))
    d = ImageDraw.Draw(pat)
    for x in range(-size, size, stripe_w*2):
        d.line([(x,size),(x+size,0)], fill=color, width=stripe_w)
    return pat

def make_checkerboard(size, color, block):
    pat = Image.new("RGBA", (size,size), (0,0,0,0))
    d = ImageDraw.Draw(pat)
    for y in range(0, size, block):
        for x in range(0, size, block):
            if ((x//block)+(y//block))%2==0:
                d.rectangle([x,y,x+block,y+block], fill=color)
    return pat

def part_ui(name, def1, def2):
    """Create all controls for one part and return their values."""
    st.header(name)
    ftype = st.selectbox(f"{name} fill type", ["Solid","Linear","Radial"], key=f"{name}_fill")
    c1 = st.color_picker(f"{name} primary", def1, key=f"{name}_c1")
    c2 = c1 if ftype=="Solid" else st.color_picker(f"{name} secondary", def2, key=f"{name}_c2")

    pat = st.selectbox(f"{name} pattern",
                       ["None","Stripes","Spots","Diagonal Stripes","Checkerboard","Custom"],
                       key=f"{name}_pat")

    # pattern parameters
    pc = sw = dr = sp = dw = bl = None
    up = None
    if pat=="Stripes":
        pc = st.color_picker(f"{name} stripe color", def2, key=f"{name}_pc")
        sw = st.slider(f"{name} stripe width", 2, 100, 20, key=f"{name}_sw")
    elif pat=="Spots":
        pc = st.color_picker(f"{name} spot color", def2, key=f"{name}_pc")
        dr = st.slider(f"{name} dot radius", 2, 100, 15, key=f"{name}_dr")
        sp = st.slider(f"{name} spacing", 10, 200, 60, key=f"{name}_sp")
    elif pat=="Diagonal Stripes":
        pc = st.color_picker(f"{name} diag color", def2, key=f"{name}_pc")
        dw = st.slider(f"{name} diag width", 2, 100, 20, key=f"{name}_dw")
    elif pat=="Checkerboard":
        pc = st.color_picker(f"{name} checker color", def2, key=f"{name}_pc")
        bl = st.slider(f"{name} block size", 5, 200, 50, key=f"{name}_bl")
    elif pat=="Custom":
        up = st.file_uploader(f"{name} tile PNG", type="png", key=f"{name}_up")

    opacity = st.slider(f"{name} pattern opacity", 0.0, 1.0, 1.0, key=f"{name}_opa")
    return ftype, c1, c2, pat, pc, sw, dr, sp, dw, bl, up, opacity

# ─── Sidebar & Randomize ────────────────────────────────────────────────────
if st.button("🎲 Randomize all"):
    for key, vals in {
        "Backpack_fill": ["Solid","Linear","Radial"],
        "Body_fill":    ["Solid","Linear","Radial"],
        "Hands_fill":   ["Solid","Linear","Radial"],
        "Backpack_pat": ["None","Stripes","Spots","Diagonal Stripes","Checkerboard"],
        "Body_pat":     ["None","Stripes","Spots","Diagonal Stripes","Checkerboard"],
        "Hands_pat":    ["None","Stripes","Spots","Diagonal Stripes","Checkerboard"],
    }.items():
        st.session_state[key] = random.choice(vals)
    # random colors
    for part in ["bp","bd","h"]:
        st.session_state[f"{part}_c1"] = "#{:06x}".format(random.randint(0,0xFFFFFF))
        st.session_state[f"{part}_c2"] = "#{:06x}".format(random.randint(0,0xFFFFFF))
        st.session_state[f"{part}_pc"] = "#{:06x}".format(random.randint(0,0xFFFFFF))
        st.session_state[f"{part}_sw"] = random.randint(5,50)
        st.session_state[f"{part}_dr"] = random.randint(5,50)
        st.session_state[f"{part}_sp"] = random.randint(20,100)
        st.session_state[f"{part}_dw"] = random.randint(5,50)
        st.session_state[f"{part}_bl"] = random.randint(20,100)
        st.session_state[f"{part}_opa"]= round(random.random(),2)

with st.sidebar:
    bp = part_ui("Backpack", "#A0522D", "#8B4513")
    st.markdown("---")
    bd = part_ui("Body",     "#FFD39F", "#FFC071")
    st.markdown("---")
    h  = part_ui("Hands",    "#A0522D", "#8B4513")
    st.markdown("---")
    st.header("Outline & Position")
    outline_color     = st.color_picker("Outline color", "#000000")
    outline_width     = st.slider("Outline width", 0, 50, 10)
    backpack_offset_y = st.slider("Backpack Y offset", -300, 300, -150)
    hand_offset_x     = st.slider("Hands X offset",      0, 300, 180)
    hand_offset_y     = st.slider("Hands Y offset",      0, 300, 220)
    st.markdown("---")
    preview_size      = st.slider("Preview size", 128, 512, 256)
    download_res      = st.selectbox("Download resolution", [256,512,1024,2048], index=1)
    file_format       = st.selectbox("File format", ["PNG","JPEG"])
    st.markdown("---")
    bg_file           = st.file_uploader("Optional background (PNG)", type="png")

# ─── Prepare background ──────────────────────────────────────────────────────
bg = None
if bg_file:
    bg = Image.open(bg_file).convert("RGBA").resize((1024,1024), Image.Resampling.LANCZOS)

# ─── Draw Canvas ─────────────────────────────────────────────────────────────
canvas = Image.new("RGBA", (1024,1024), (0,0,0,0))

for (ftype,c1,c2,pat,pc,sw,dr,sp,dw,bl,up,opa), center, r in [
    (bp, (512,512+backpack_offset_y), 240),
    (bd, (512,512),                280),
    (h,  (512-hand_offset_x,512+hand_offset_y), 100),
    (h,  (512+hand_offset_x,512+hand_offset_y), 100),
]:
    # base fill
    fill_img = get_fill_image(ftype, c1, c2, 2*r).convert("RGBA")

    # build pattern
    pattern = None
    if   pat=="Stripes":          pattern = make_stripes(2*r, pc, sw)
    elif pat=="Spots":            pattern = make_spots(2*r, pc, dr, sp)
    elif pat=="Diagonal Stripes": pattern = make_diagonal_stripes(2*r, pc, dw)
    elif pat=="Checkerboard":     pattern = make_checkerboard(2*r, pc, bl)
    elif pat=="Custom" and up:
        tile = Image.open(up).convert("RGBA")
        # scale tile to 20% of diameter
        dia = 2*r
        nw = max(1, int(dia*0.2))
        nh = int(nw * tile.height / tile.width)
        tile_small = tile.resize((nw,nh), Image.Resampling.LANCZOS)
        pattern    = Image.new("RGBA", (dia,dia), (0,0,0,0))
        for y in range(0, dia, nh):
            for x in range(0, dia, nw):
                pattern.paste(tile_small, (x,y), tile_small)

    # overlay pattern with opacity
    if pattern:
        # adjust alpha
        alpha_mask = pattern.split()[3].point(lambda p: int(p*opa))
        pattern.putalpha(alpha_mask)
        fill_img = Image.alpha_composite(fill_img, pattern)

    # paste circle onto canvas
    mask = Image.new("L", (2*r,2*r), 0)
    ImageDraw.Draw(mask).ellipse((0,0,2*r,2*r), fill=255)
    canvas.paste(fill_img, (center[0]-r, center[1]-r), mask)

    # outline
    ImageDraw.Draw(canvas).ellipse(
        (center[0]-r, center[1]-r, center[0]+r, center[1]+r),
        outline=outline_color, width=outline_width
    )

# background underneath
if bg:
    canvas = Image.alpha_composite(bg, canvas)

# ─── Preview ────────────────────────────────────────────────────────────────
preview = canvas.resize((preview_size, preview_size), Image.Resampling.LANCZOS)
st.subheader("Preview")
st.image(preview)

# ─── Download Skin ──────────────────────────────────────────────────────────
out = canvas.resize((download_res, download_res), Image.Resampling.LANCZOS)
buf = io.BytesIO()
if file_format=="PNG":
    out.save(buf, "PNG")
    mime = "image/png"
else:
    out.convert("RGB").save(buf, "JPEG")
    mime = "image/jpeg"
buf.seek(0)
st.download_button("Download Skin", buf,
                   file_name=f"survev_skin.{file_format.lower()}",
                   mime=mime)

# ─── Download Config (JSON) ─────────────────────────────────────────────────
config = {
    "backpack": {"fill":bp[0], "primary":bp[1], "secondary":bp[2],
                 "pattern":bp[3], "pattern_color":bp[4], "stripe_width":bp[5],
                 "dot_radius":bp[6], "spacing":bp[7], "diag_width":bp[8],
                 "block":bp[9], "pattern_opacity":bp[10]},
    "body":     {"fill":bd[0], "primary":bd[1], "secondary":bd[2],
                 "pattern":bd[3], "pattern_color":bd[4], "stripe_width":bd[5],
                 "dot_radius":bd[6], "spacing":bd[7], "diag_width":bd[8],
                 "block":bd[9], "pattern_opacity":bd[10]},
    "hands":    {"fill":h[0],  "primary":h[1],  "secondary":h[2],
                 "pattern":h[3], "pattern_color":h[4], "stripe_width":h[5],
                 "dot_radius":h[6], "spacing":h[7], "diag_width":h[8],
                 "block":h[9], "pattern_opacity":h[10]},
    "outline_color": outline_color,
    "outline_width": outline_width,
    "offsets": {"backpack_y":backpack_offset_y,
                "hands_x":hand_offset_x, "hands_y":hand_offset_y},
    "download": {"resolution": download_res, "format": file_format}
}
json_str = json.dumps(config, indent=2)
st.download_button("Download config (JSON)",
                   data=json_str,
                   file_name="skin_config.json",
                   mime="application/json")

# ─── Download as SVG ────────────────────────────────────────────────────────
# embed PNG as base64
png_buf = io.BytesIO()
out.save(png_buf, "PNG")
b64 = base64.b64encode(png_buf.getvalue()).decode()
svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'width="{download_res}" height="{download_res}">'
    f'<image href="data:image/png;base64,{b64}" '
    f'width="{download_res}" height="{download_res}" /></svg>'
)
st.download_button("Download as SVG",
                   data=svg,
                   file_name="skin.svg",
                   mime="image/svg+xml")
