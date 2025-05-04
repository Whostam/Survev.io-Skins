import streamlit as st
from PIL import Image, ImageDraw
import io, random, json, base64

# Page config
st.set_page_config(page_title="Survev.io Skin Editor", layout="wide")
st.title("🎨 Survev.io Skin Editor")
st.write("Use the sidebar (or the 🎲 Randomize button) to customize or auto‑generate a skin.")

# Utility: random hex color
def random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)

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
    if ftype == "Solid": return Image.new("RGB", (size, size), c1)
    if ftype == "Linear": return make_linear_gradient(size, c1, c2)
    return make_radial_gradient(size, c1, c2)

# ─── Built-in pattern generators ────────────────────────────────────────────
def make_stripes(size,color,stripe_w):
    pat=Image.new("RGBA",(size,size),(0,0,0,0)); d=ImageDraw.Draw(pat)
    for x in range(0,size,stripe_w*2): d.rectangle([x,0,x+stripe_w,size],fill=color)
    return pat

def make_spots(size,color,dot_r,spacing):
    pat=Image.new("RGBA",(size,size),(0,0,0,0)); d=ImageDraw.Draw(pat)
    for y in range(0,size,spacing):
        for x in range(0,size,spacing): d.ellipse([x,y,x+dot_r,y+dot_r],fill=color)
    return pat

def make_diagonal_stripes(size,color,stripe_w):
    pat=Image.new("RGBA",(size,size),(0,0,0,0)); d=ImageDraw.Draw(pat)
    for x in range(-size,size,stripe_w*2): d.line([(x,size),(x+size,0)],fill=color,width=stripe_w)
    return pat

def make_checkerboard(size,color,block):
    pat=Image.new("RGBA",(size,size),(0,0,0,0)); d=ImageDraw.Draw(pat)
    for y in range(0,size,block):
        for x in range(0,size,block):
            if ((x//block)+(y//block))%2==0: d.rectangle([x,y,x+block,y+block],fill=color)
    return pat

# ─── Sidebar & Randomize ───────────────────────────────────────────────────
randomize = st.sidebar.button("🎲 Randomize Skin")
def init_random():
    if randomize:
        for name in ["Backpack","Body","Hands"]:
            st.session_state[f"{name}_fill"]    = random.choice(["Solid","Linear","Radial"])
            st.session_state[f"{name}_c1"]      = random_color()
            st.session_state[f"{name}_c2"]      = random_color()
            st.session_state[f"{name}_pat"]     = random.choice(["None","Stripes","Spots","Diagonal Stripes","Checkerboard","Custom"])
            st.session_state[f"{name}_pc"]      = random_color()
            st.session_state[f"{name}_stripe_w"] = random.randint(5,50)
            st.session_state[f"{name}_dot_r"]    = random.randint(5,30)
            st.session_state[f"{name}_spacing"]  = random.randint(20,100)
            st.session_state[f"{name}_diag_w"]   = random.randint(5,50)
            st.session_state[f"{name}_block"]    = random.randint(20,80)
            st.session_state[f"{name}_up"]       = None
init_random()

with st.sidebar:
    def part_ui(name,def1,def2):
        st.header(name)
        f=st.selectbox("Fill type",["Solid","Linear","Radial"],key=f"{name}_fill")
        c1=st.color_picker("Primary",def1,key=f"{name}_c1")
        c2=c1 if f=="Solid" else st.color_picker("Secondary",def2,key=f"{name}_c2")
        p=st.selectbox("Pattern",["None","Stripes","Spots","Diagonal Stripes","Checkerboard","Custom"],key=f"{name}_pat")
        pc=sw=dr=sp=dw=bl=up=None
        if p=="Stripes": pc=st.color_picker("Stripe color",def2,key=f"{name}_pc"); sw=st.slider("Width",1,100,st.session_state.get(f"{name}_stripe_w",20),key=f"{name}_stripe_w")
        elif p=="Spots": pc=st.color_picker("Spot color",def2,key=f"{name}_pc"); dr=st.slider("Radius",1,50,st.session_state.get(f"{name}_dot_r",15),key=f"{name}_dot_r"); sp=st.slider("Spacing",5,200,st.session_state.get(f"{name}_spacing",60),key=f"{name}_spacing")
        elif p=="Diagonal Stripes": pc=st.color_picker("Diag color",def2,key=f"{name}_pc"); dw=st.slider("Width",1,100,st.session_state.get(f"{name}_diag_w",20),key=f"{name}_diag_w")
        elif p=="Checkerboard": pc=st.color_picker("Check color",def2,key=f"{name}_pc"); bl=st.slider("Block size",5,200,st.session_state.get(f"{name}_block",50),key=f"{name}_block")
        elif p=="Custom": up=st.file_uploader("Tile PNG",type="png",key=f"{name}_up")
        return f,c1,c2,p,pc,sw,dr,sp,dw,bl,up
    bp=part_ui("Backpack","#A0522D","#8B4513"); st.markdown("---")
    bd=part_ui("Body","#FFD39F","#FFC071"); st.markdown("---")
    hd=part_ui("Hands","#A0522D","#8B4513"); st.markdown("---")
    oc=st.color_picker("Outline","#000000"); ow=st.slider("Outline width",0,50,10)
    by=st.slider("Backpack Y offset",-300,300,-150); hx=st.slider("Hands X offset",0,300,180); hy=st.slider("Hands Y offset",0,300,220)
    st.markdown("---"); bg=st.file_uploader("Background PNG",type="png")

# Load background
bg_img=None
if bg: bg_img=Image.open(bg).convert("RGBA").resize((1024,1024),Image.Resampling.LANCZOS)
# Build canvas
canvas=Image.new("RGBA",(1024,1024),(0,0,0,0))
for data in [(*bp,(512,512+by),240),(*bd,(512,512),280),(*hd,(512-hx,512+hy),100),(*hd,(512+hx,512+hy),100)]:
    ftype,c1,c2,p,pc,sw,dr,sp,dw,bl,up,center,r=data
    img=get_fill_image(ftype,c1,c2,2*r).convert("RGBA")
    pattern=None
    if p=="Stripes": pattern=make_stripes(2*r,pc,sw)
    elif p=="Spots": pattern=make_spots(2*r,pc,dr,sp)
    elif p=="Diagonal Stripes": pattern=make_diagonal_stripes(2*r,pc,dw)
    elif p=="Checkerboard": pattern=make_checkerboard(2*r,pc,bl)
    elif p=="Custom" and up:
        tile=Image.open(up).convert("RGBA"); ow,oh=tile.size; dia=2*r; nw=int(dia*0.2); nh=int(nw*(oh/ow)); tsm=tile.resize((nw,nh),Image.Resampling.LANCZOS)
        pattern=Image.new("RGBA",(dia,dia),(0,0,0,0))
        for y in range(0,dia,nh):
            for x in range(0,dia,nw): pattern.paste(tsm,(x,y),tsm)
    if pattern: img.paste(pattern,(0,0),pattern)
    mask=Image.new("L",(2*r,2*r),0); md=ImageDraw.Draw(mask); md.ellipse((0,0,2*r,2*r),fill=255)
    canvas.paste(img,(center[0]-r,center[1]-r),mask)
    ImageDraw.Draw(canvas).ellipse((center[0]-r,center[1]-r,center[0]+r,center[1]+r),outline=oc,width=ow)
if bg_img: canvas=Image.alpha_composite(bg_img,canvas)

# Preview
ps=st.selectbox("Preview size",[320,400,512],index=0)
st.subheader("Preview")
st.image(canvas.resize((ps,ps),Image.Resampling.LANCZOS))

# Prepare config JSON
config = {
    "Backpack": {"fill":bp[0],"c1":bp[1],"c2":bp[2],"pattern":bp[3],"pattern_color":bp[4],
                 "stripe_w":bp[5],"dot_r":bp[6],"spacing":bp[7],"diag_w":bp[8],"block":bp[9]},
    "Body":     {"fill":bd[0],"c1":bd[1],"c2":bd[2],"pattern":bd[3],"pattern_color":bd[4],
                 "stripe_w":bd[5],"dot_r":bd[6],"spacing":bd[7],"diag_w":bd[8],"block":bd[9]},
    "Hands":    {"fill":hd[0],"c1":hd[1],"c2":hd[2],"pattern":hd[3],"pattern_color":hd[4],
                 "stripe_w":hd[5],"dot_r":hd[6],"spacing":hd[7],"diag_w":hd[8],"block":hd[9]},
    "outline": {"color":oc,"width":ow},
    "offsets": {"backpack_y":by,"hands_x":hx,"hands_y":hy}
}
json_buf = io.StringIO()
json.dump(config, json_buf, indent=2)
json_buf.seek(0)
st.download_button("Download config (JSON)", data=json_buf.getvalue(), file_name="skin_config.json", mime="application/json")

# Download options
dr=st.selectbox("Download resolution",[256,512,1024],index=1)
fm=st.selectbox("File format",["PNG","JPEG","SVG"],index=0)
out_img = canvas.resize((dr,dr),Image.Resampling.LANCZOS)

# Handle SVG embedding a PNG
if fm=="SVG":
    buf=io.BytesIO(); out_img.save(buf, format="PNG"); b64=base64.b64encode(buf.getvalue()).decode()
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{dr}" height="{dr}">' \
          f'<image href="data:image/png;base64,{b64}" width="{dr}" height="{dr}"/>' \
          '</svg>'
    st.download_button("Download Skin (SVG)", data=svg, file_name="survev_skin.svg", mime="image/svg+xml")
else:
    buf=io.BytesIO()
    if fm=="JPEG": out_img.convert("RGB").save(buf,format="JPEG")
    else:           out_img.save(buf,format="PNG")
    buf.seek(0)
    st.download_button("Download Skin", data=buf, file_name=f"survev_skin.{fm.lower()}", mime=f"image/{fm.lower()}")
