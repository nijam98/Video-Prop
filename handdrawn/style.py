import cv2, numpy as np
W,H=1080,1920
rng=np.random.default_rng(7)

def make_paper():
    n=rng.normal(0,1,(H//4,W//4)).astype(np.float32)
    n=cv2.resize(cv2.GaussianBlur(n,(0,0),2),(W,H),interpolation=cv2.INTER_CUBIC)
    f=rng.normal(0,1,(H,W)).astype(np.float32)
    f=cv2.GaussianBlur(f,(0,0),0.7)
    # long fibres
    fib=cv2.filter2D(rng.normal(0,1,(H,W)).astype(np.float32),-1,np.ones((1,15),np.float32)/15)
    p=1.0+0.035*n/np.abs(n).max()+0.03*f/np.abs(f).max()+0.03*fib/np.abs(fib).max()
    tint=np.array([0.93,0.97,1.0],np.float32)  # BGR warm cream
    return (p[...,None]*tint).astype(np.float32)
PAPER=make_paper()

def make_hatch(dirn,spacing):
    img=np.full((H,W),0,np.float32)
    for c in range(-H,W+H,spacing):
        if dirn==0: p1,p2=(c,0),(c+H,H)
        else: p1,p2=(c,H),(c+H,0)
        jitter=rng.normal(0,0.6)
        cv2.line(img,(int(p1[0]+jitter),p1[1]),(int(p2[0]+jitter),p2[1]),1.0,1,cv2.LINE_AA)
    img=cv2.GaussianBlur(img,(0,0),0.6)
    # break the strokes so it looks pencil
    brk=cv2.resize(rng.random((H//6,W//6)).astype(np.float32),(W,H))
    return img*(0.5+0.5*brk)
HATCH1=make_hatch(0,11); HATCH2=make_hatch(1,13)

def noise_field(seed):
    r=np.random.default_rng(seed)
    dx=cv2.resize(r.normal(0,1,(H//48,W//48)).astype(np.float32),(W,H),interpolation=cv2.INTER_CUBIC)
    dy=cv2.resize(r.normal(0,1,(H//48,W//48)).astype(np.float32),(W,H),interpolation=cv2.INTER_CUBIC)
    return dx,dy
GX,GY=np.meshgrid(np.arange(W,dtype=np.float32),np.arange(H,dtype=np.float32))
FIELDS=[noise_field(s) for s in range(6)]

CLAHE=cv2.createCLAHE(clipLimit=2.5,tileGridSize=(8,8))
def edge_lines(gray_u8,sigma=1.1,k=1.7,t=0.012,soft=0.02):
    g=CLAHE.apply(gray_u8).astype(np.float32)/255
    g1=cv2.GaussianBlur(g,(0,0),sigma); g2=cv2.GaussianBlur(g,(0,0),sigma*k)
    d=g2-g1   # positive on dark side of an edge
    a=np.clip((d-t)/soft,0,1)
    return (1-0.9*a).astype(np.float32)
def stylize(bgr,fidx):
    """bgr: uint8 HxW full-res frame. returns uint8."""
    small=cv2.resize(bgr,(W//2,H//2),interpolation=cv2.INTER_AREA)
    c=small
    for _ in range(2): c=cv2.bilateralFilter(c,9,40,7)
    lab=cv2.cvtColor(c,cv2.COLOR_BGR2LAB).astype(np.float32)
    L=lab[...,0]/255.0
    # soft posterize lightness (cel-ish washes)
    q=6; Ls=L*q; base=np.floor(Ls); frac=Ls-base
    frac=np.clip((frac-0.35)/0.3,0,1); frac=frac*frac*(3-2*frac)
    Lp=(base+frac)/q
    Lp=0.35*Lp+0.65*L
    Lp=0.05+0.95*Lp  # lift shadows like watercolor on paper
    lab[...,0]=Lp*255
    lab[...,1:]=(lab[...,1:]-128)*1.25+128
    col=cv2.cvtColor(np.clip(lab,0,255).astype(np.uint8),cv2.COLOR_LAB2BGR)
    col=cv2.resize(col,(W,H),interpolation=cv2.INTER_CUBIC).astype(np.float32)/255
    # line art from full res
    gray=cv2.cvtColor(bgr,cv2.COLOR_BGR2GRAY)
    gray=cv2.bilateralFilter(gray,7,25,5)
    lines=edge_lines(gray)
    # boil: shift line art with a field that changes every 5 frames (12fps hand-drawn feel)
    dx,dy=FIELDS[(fidx//5)%len(FIELDS)]
    lines=cv2.remap(lines,GX+1.6*dx,GY+1.6*dy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    # pencil hatching in shadows
    Lf=cv2.resize(L,(W,H))
    sh1=np.clip((0.45-Lf)/0.25,0,1); sh2=np.clip((0.28-Lf)/0.2,0,1)
    o=(fidx//5)%3
    h1=np.roll(HATCH1,o,axis=1); h2=np.roll(HATCH2,o,axis=0)
    hatchmask=1-0.45*sh1*h1-0.45*sh2*h2
    # keep the lighting: glow from bright light sources of the original frame
    of=bgr.astype(np.float32)/255
    lum=of.max(2)
    bright=np.clip((lum-0.78)/0.22,0,1)
    glow=cv2.GaussianBlur(of*bright[...,None],(0,0),18)*0.9+cv2.GaussianBlur(of*bright[...,None],(0,0),5)*0.5
    out=col*PAPER
    out*=hatchmask[...,None]
    ink=np.array([0.22,0.2,0.2],np.float32)
    out=out*lines[...,None]**2+(1-lines[...,None])*ink  # ink lines over the wash
    # light shines over the ink: bright lights stay bright, plus soft bloom
    out=np.maximum(out, of*bright[...,None]*0.95+out*(1-bright[...,None]))
    out=1-(1-out)*(1-np.clip(glow,0,1))
    return np.clip(out*255,0,255).astype(np.uint8)
