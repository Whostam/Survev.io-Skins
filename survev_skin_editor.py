import streamlit as st
from PIL import Image, ImageDraw
import io, random, json

# ─── Page config & Theme toggle ─────────────────────────────────────────────
st.set_page_config(page_title="Survev.io Skin Editor", layout="wide")

# Day/Night mode
mode = st.sidebar.radio("Mode", ["Day", "Night"])
# Adjust background brightness and panel overlay based on mode
if mode == "Day":
    bg_brightness = 0.7
    panel_bg = "rgba(255,255,255,0.85)"
else:
    bg_brightness = 0.3
    panel_bg = "rgba(0,0,0,0.6)"

# ─── Branding ────────────────────────────────────────────────────────────────
# Sidebar logo from static/
st.sidebar.markdown(
    "<img src='/static/logo.png' width='120' alt='Logo'/>",
    unsafe_allow_html=True
)

# Blurred fullscreen background CSS
st.markdown(
    f"""
    <style>
      .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        background: url('/static/main_splash_rivers.png') center/cover no-repeat;
        filter: blur(8px) brightness({bg_brightness});
        z-index: -1;
      }}
      .block-container, .sidebar-content {{
        background-color: {panel_bg} !important;
      }}
    </style>
    """,
    unsafe_allow_html=True
)

# Title
st.title("🎨 Survev.io Skin Editor")
st.write("Use the sidebar (or the 🎲 Randomize button) to customize or auto-generate a skin.")

# ─── Utility: random color ────────────────────────────────────────────────────
def random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)

# ─── Gradient helpers ────────────────────────────────────────────────────────
def make_linear_gradient(size, c1, c2):
    base = Image.new("RGB", (1, size)); d = ImageDraw.Draw(base)
    for y in range(size):
        t = y/(size-1)
        r = int((1-t)*int(c1[1:3],16) + t*int(c2[1:3],16))
        g = int((1-t)*int(c1[3:5],16) + t*int(c2[3:5],16))
        b = int((1-t)*int(c1[5:7],16) + t*int(c2[5:7],16))
        d.point((0,y),(r,g,b))
    return base.resize((size,size))

def make_radial_gradient(size, c1, c2):
    img = Image.new("RGB",(size,size)); d = ImageDraw.Draw(img)
    cx = cy = size//2; maxr = (2**0.5)*(size/2)
    for y in range(size):
        for x in range(size):
            d0 = ((x-cx)**2 + (y-cy)**2)**0.5 / maxr
            t = min(d0,1)
            r = int((1-t)*int(c1[1:3],16) + t*int(c2[1:3],16))
            g = int((1-t)*int(c1[3:5],16) + t*int(c2[3:5],16))
            b = int((1-t)*int(c1[5:7],16) + t*int(c2[5:7],16))
            d.point((x,y),(r,g,b))
    return img

def get_fill_image(ftype, c1, c2, size):
    if ftype=="Solid":  return Image.new("RGB",(size,size),c1)
    if ftype=="Linear": return make_linear_gradient(size,c1,c2)
    return make_radial_gradient(size,c1,c2)

# ─── Patterns ───────────────────────────────────────────────────────────────
def make_stripes(sz,col,w):
    p = Image.new("RGBA",(sz,sz),(0,0,0,0)); d=ImageDraw.Draw(p)
    for x in range(0,sz,w*2): d.rectangle([x,0,x+w,sz],fill=col)
    return p

def make_spots(sz,col,dr,sp):
    p = Image.new("RGBA",(sz,sz),(0,0,0,0)); d=ImageDraw.Draw(p)
    for y in range(0,sz,sp):
        for x in range(0,sz,sp): d.ellipse([x,y,x+dr,y+dr],fill=col)
    return p

def make_diagonal(sz,col,w):
    p = Image.new("RGBA",(sz,sz),(0,0,0,0)); d=ImageDraw.Draw(p)
    for x in range(-sz,sz,w*2): d.line([(x,sz),(x+sz,0)],fill=col,width=w)
    return p

def make_checker(sz,col,b):
    p = Image.new("RGBA",(sz,sz),(0,0,0,0)); d=ImageDraw.Draw(p)
    for y in range(0,sz,b):
        for x in range(0,sz,b):
            if ((x//b+y//b)%2)==0: d.rectangle([x,y,x+b,y+b],fill=col)
    return p

# ─── Sidebar Controls & Randomizer ─────────────────────────────────────────
rand = st.sidebar.button("🎲 Randomize Skin")
if rand:
    for part in ["Backpack","Body","Hands"]:
        st.session_state[f"{part}_fill"] = random.choice(["Solid","Linear","Radial"])
        st.session_state[f"{part}_c1"]   = random_color()
        st.session_state[f"{part}_c2"]   = random_color()
        st.session_state[f"{part}_pat"]  = random.choice(["None","Stripes","Spots","Diagonal","Checker","Custom"])
        st.session_state[f"{part}_pc"]   = random_color()
        st.session_state[f"{part}_sw"]   = random.randint(5,50)
        st.session_state[f"{part}_dr"]   = random.randint(5,30)
        st.session_state[f"{part}_sp"]   = random.randint(20,100)
        st.session_state[f"{part}_dw"]   = random.randint(5,50)
        st.session_state[f"{part}_bl"]   = random.randint(20,80)
        st.session_state[f"{part}_alpha"] = round(random.random(),2)

def part_ui(name, d1, d2):
    st.sidebar.header(name)
    f = st.sidebar.selectbox("Fill type", ["Solid","Linear","Radial"], key=f"{name}_fill")
    c1 = st.sidebar.color_picker("Primary color", d1, key=f"{name}_c1")
    c2 = c1 if f=="Solid" else st.sidebar.color_picker("Secondary color", d2, key=f"{name}_c2")
    p  = st.sidebar.selectbox("Pattern", ["None","Stripes","Spots","Diagonal","Checker","Custom"], key=f"{name}_pat")
    pc=sw=dr=sp=dw=bl=up=None
    if p=="Stripes":  pc=st.sidebar.color_picker("Stripe col",d2,key=f"{name}_pc"); sw=st.sidebar.slider("W",1,100,20,key=f"{name}_sw")
    if p=="Spots":    pc=st.sidebar.color_picker("Spot col",d2,key=f"{name}_pc"); dr=st.sidebar.slider("R",1,50,15,key=f"{name}_dr"); sp=st.sidebar.slider("Sp",5,200,60,key=f"{name}_sp")
    if p=="Diagonal": pc=st.sidebar.color_picker("Diag col",d2,key=f"{name}_pc"); dw=st.sidebar.slider("W",1,100,20,key=f"{name}_dw")
    if p=="Checker":  pc=st.sidebar.color_picker("Chk col",d2,key=f"{name}_pc"); bl=st.sidebar.slider("B",5,200,50,key=f"{name}_bl")
    if p=="Custom":   up=st.sidebar.file_uploader("Tile PNG",type="png",key=f"{name}_up")
    alpha = st.sidebar.slider("Opacity",0.0,1.0,1.0,key=f"{name}_alpha")
    return f,c1,c2,p,pc,sw,dr,sp,dw,bl,up,alpha

bp = part_ui("Backpack","#A0522D","#8B4513")
bd = part_ui("Body","#FFD39F","#FFC071")
hd = part_ui("Hands","#A0522D","#8B4513")

oc = st.sidebar.color_picker("Outline color", "#000000")
ow = st.sidebar.slider("Outline width", 0,50,10)
by = st.sidebar.slider("Backpack Y", -300,300,-150)
hx = st.sidebar.slider("Hands X", 0,300,180)
hy = st.sidebar.slider("Hands Y", 0,300,220)
bg_file = st.sidebar.file_uploader("Optional BG (PNG)", type="png")

# ─── Canvas ────────────────────────────────────────────────────────────────
bg = None
if bg_file:
    bg = Image.open(bg_file).convert("RGBA").resize((1024,1024), Image.Resampling.LANCZOS)

canvas = Image.new("RGBA",(1024,1024),(0,0,0,0))
for data,ctr,r in [(bp,(512,512+by),240),(bd,(512,512),280),(hd,(512-hx,512+hy),100),(hd,(512+hx,512+hy),100)]:
    f,c1,c2,p,pc,sw,dr,sp,dw,bl,up,alpha = data
    base = get_fill_image(f,c1,c2,2*r).convert("RGBA")
    pat_img = None
    if p=="Stripes":  pat_img=make_stripes(2*r,pc,sw)
    elif p=="Spots":  pat_img=make_spots(2*r,pc,dr,sp)
    elif p=="Diagonal":pat_img=make_diagonal(2*r,pc,dw)
    elif p=="Checker": pat_img=make_checker(2*r,pc,bl)
    elif p=="Custom" and up:
        tile=Image.open(up).convert("RGBA"); ow_t,oh_t=tile.size;nw=int(2*r*0.2);nh=int(nw*oh_t/ow_t)
        small=tile.resize((nw,nh),Image.Resampling.LANCZOS)
        pat_img=Image.new("RGBA",(2*r,2*r),(0,0,0,0))
        for yy in range(0,2*r,nh):
            for xx in range(0,2*r,nw): pat_img.paste(small,(xx,yy),small)
    if pat_img:
        msk=pat_img.split()[3].point(lambda px:int(px*alpha)); pat_img.putalpha(msk)
        base=Image.alpha_composite(base,pat_img)
    m = Image.new("L",(2*r,2*r),0); ImageDraw.Draw(m).ellipse((0,0,2*r,2*r),fill=255)
    canvas.paste(base,(ctr[0]-r,ctr[1]-r),m)
    ImageDraw.Draw(canvas).ellipse((ctr[0]-r,ctr[1]-r,ctr[0]+r,ctr[1]+r),outline=oc,width=ow)

if bg: canvas = Image.alpha_composite(bg,canvas)

# ─── Preview & Export ───────────────────────────────────────────────────────
st.subheader("Preview")
ps = st.selectbox("Preview size",[256,320,512],index=1)
st.image(canvas.resize((ps,ps),Image.Resampling.LANCZOS))

col1,col2=st.columns(2)
with col1:
    res=st.selectbox("Resolution",[256,512,1024],index=1)
    fmt=st.selectbox("Format",["PNG","JPEG","SVG"],index=0)
    out=canvas.resize((res,res),Image.Resampling.LANCZOS)
    buf=io.BytesIO(); mime='image/png'
    if fmt=='JPEG': out.convert("RGB").save(buf,"JPEG"); mime='image/jpeg'
    else: out.save(buf,"PNG")
    buf.seek(0)
    st.download_button("Download Skin",data=buf,file_name=f"skin.{fmt.lower()}",mime=mime)
with col2:
    cfg={}
    for nm,dt in zip(["Backpack","Body","Hands"],[bp,bd,hd]):
        f,c1,c2,p,pc,sw,dr,sp,dw,bl,up,alpha=dt
        cfg[nm]={'fill':f,'c1':c1,'c2':c2,'pattern':p,'pattern_col':pc,'sw':sw,'dr':dr,'sp':sp,'dw':dw,'bl':bl,'alpha':alpha}
    cfg['outline']={'color':oc,'width':ow}
    cfg['offsets']={'by':by,'hx':hx,'hy':hy}
    st.download_button("Download Config (JSON)",data=json.dumps(cfg,indent=2),file_name="config.json",mime="application/json")
