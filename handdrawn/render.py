import json, subprocess, sys, numpy as np, cv2, math
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0,".")
W,H,FPS,N=1080,1920,60,3600
E=json.load(open("work/edl.json")); T=E["tempo"]
SEC={s["name"]:s for s in E["sections"]}
MARK="fonts/PermanentMarker-Regular.ttf"; CAV="fonts/Caveat.ttf"
def at(sec,src_t):
    """final-timeline seconds for a source time inside a section's audio"""
    s=SEC[sec]; acc=s["start"]
    for a,b in s["audio"]:
        if a<=src_t<=b: return (acc+src_t-a)/T
        acc+=b-a
    return (acc)/T
def end(sec): return (SEC[sec]["start"]+SEC[sec]["dur"])/T
# captions: (t0,t1,text,kind,y)
C=[]
C+= [(0.0,end("hook"),"MACAM MANA TENGOK,","hook_s",430),
     (at("hook",94.9),end("hook"),"MACAM TU DAPAT!","hook_s",530),
     (at("hook",95.6),end("hook"),"MASUK","hook",760),
     (at("hook",96.0),end("hook"),"CUCI KAKI!","hook",920)]
C+= [(at("intro",2.4),end("intro"),"EVOKE KONDOMINIUM","title",360),
     (at("intro",3.9),end("intro"),"PERMATA PAUH","title",470),
     (at("intro",6.5),at("spec",10.2),"FULLY FURNISHED","tag",1250)]
def lst(sec,items,y0=1080,step=118):
    for i,(st,txt) in enumerate(items): C.append((at(sec,st),end(sec),txt,"item",y0+i*step))
lst("spec",[(10.3,"1140 KAKI PERSEGI"),(14.4,"FREEHOLD - NON BUMI LOT"),(16.4,"3 BILIK + 2 BILIK AIR"),(19.0,"LEVEL 10")])
lst("park",[(24.0,"2 PARKING KERETA"),(26.1,"+ 1 PARKING MOTOR"),(29.4,"MAINTENANCE ±RM330")])
lst("reno",[(43.9,"RENOVATION SIAP"),(49.1,"QUARTZ STONE"),(51.9,"WET + DRY KITCHEN")])
lst("furn",[(74.2,"4 UNIT AIRCON"),(77.2,"TV + KABINET TV"),(79.2,"MESIN BASUH"),(79.8,"MICROWAVE")])
lst("loc",[(99.1,"DEKAT UiTM"),(99.6,"POLITEKNIK"),(101.8,"HIGHWAY"),(102.6,"SESUAI INVESTMENT!")])
C+= [(at("cta",107.3),N/FPS,"LINK DI BIO","hook",620),
     (at("cta",109.2),N/FPS,"BOLEH LOAN LPPSA / BANK","tag",1250)]

STY={ "hook":(MARK,150,(255,214,10),(25,22,20),14,True),
      "hook_s":(MARK,70,(25,22,20),None,0,"hl"),
      "title":(MARK,82,(255,255,255),(25,22,20),10,False),
      "tag":(MARK,72,(25,22,20),None,0,"hl"),
      "item":(MARK,64,(25,22,20),None,0,"hl")}
rng=np.random.default_rng(3)
def render_caption(text,kind,variant):
    font,size,fill,stroke,sw,extra=STY[kind]
    f=ImageFont.truetype(font,size)
    bb=f.getbbox(text,stroke_width=sw); tw,th=bb[2]-bb[0],bb[3]-bb[1]
    pad=40; im=Image.new("RGBA",(tw+2*pad,th+2*pad),(0,0,0,0)); d=ImageDraw.Draw(im)
    r=np.random.default_rng(hash((text,variant))%2**32)
    if extra=="hl" or extra is True:
        # rough marker highlight behind text
        col=(255,224,64,235) if extra=="hl" else (25,22,20,0)
        if extra=="hl":
            for k in range(3):
                j=lambda s: int(r.normal(0,s))
                d.polygon([(pad-18+j(5),pad-6+j(4)),(pad+tw+18+j(5),pad-10+j(4)),(pad+tw+14+j(5),pad+th+12+j(4)),(pad-14+j(5),pad+th+8+j(4))],fill=col)
    d.text((pad-bb[0],pad-bb[1]),text,font=f,fill=fill,stroke_width=sw,stroke_fill=stroke)
    a=np.array(im)
    ang=r.normal(0,1.2)+(-2.5 if kind=="hook" else 0)
    M=cv2.getRotationMatrix2D((a.shape[1]/2,a.shape[0]/2),ang,1.0)
    a=cv2.warpAffine(a,M,(a.shape[1],a.shape[0]),flags=cv2.INTER_LINEAR)
    # max width
    if a.shape[1]>W-60:
        s=(W-60)/a.shape[1]; a=cv2.resize(a,None,fx=s,fy=s,interpolation=cv2.INTER_AREA)
    return a
CACHE={}
def get_cap(i,variant):
    k=(i,variant)
    if k not in CACHE: CACHE[k]=render_caption(C[i][2],C[i][3],variant)
    return CACHE[k]
def comp(frame,ov,cx,cy,scale,alpha):
    if scale!=1.0: ov=cv2.resize(ov,None,fx=scale,fy=scale,interpolation=cv2.INTER_LINEAR)
    h,w=ov.shape[:2]; x0=int(cx-w/2); y0=int(cy-h/2)
    xs,ys=max(0,x0),max(0,y0); xe,ye=min(W,x0+w),min(H,y0+h)
    if xe<=xs or ye<=ys: return
    o=ov[ys-y0:ye-y0,xs-x0:xe-x0].astype(np.float32)
    a=o[...,3:4]/255*alpha
    roi=frame[ys:ye,xs:xe].astype(np.float32)
    frame[ys:ye,xs:xe]=(roi*(1-a)+o[...,2::-1]*a).astype(np.uint8)
def pop(dt):
    if dt<0: return 0,0
    if dt<0.12: p=dt/0.12; return 0.5+0.65*p, p
    if dt<0.22: p=(dt-0.12)/0.1; return 1.15-0.15*p,1
    return 1.0,1
def overlay(frame,fi):
    t=fi/FPS
    for i,(t0,t1,txt,kind,y) in enumerate(C):
        if t0<=t<t1:
            s,a=pop(t-t0)
            if t1-t<0.15: a*=max(0,(t1-t)/0.15)
            if a<=0: continue
            v=(fi//5)%3   # hand-drawn boil on text too
            if kind=="hook": s*=1+0.025*math.sin(t*9)
            comp(frame,get_cap(i,v),W/2,y,s,a)
    return frame
def work(args):
    import style
    fi,buf=args
    f=np.frombuffer(buf,np.uint8).reshape(H,W,3)
    out=style.stylize(f,fi)
    # gentle punch-in zoom on the hook
    t=fi/FPS
    if t<end("hook"):
        z=1.0+0.06*(t/end("hook"))
        M=cv2.getRotationMatrix2D((W/2,H/2),0,z); out=cv2.warpAffine(out,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    return overlay(np.ascontiguousarray(out),fi).tobytes()
def reader():
    p=subprocess.Popen(["ffmpeg","-v","error","-i","work/cut60.mkv","-vf",f"scale={W}:{H}:flags=lanczos,tpad=stop_mode=clone:stop=30","-frames:v",str(N),"-f","rawvideo","-pix_fmt","bgr24","-"],stdout=subprocess.PIPE)
    fi=0
    while True:
        b=p.stdout.read(W*H*3)
        if len(b)<W*H*3: break
        yield fi,b; fi+=1
if __name__=="__main__":
    lim=int(sys.argv[1]) if len(sys.argv)>1 else N
    out=sys.argv[2] if len(sys.argv)>2 else "work/final.mp4"
    enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
        "-i","work/audio60.wav","-map","0:v","-map","1:a","-c:v","libx264","-preset","slow","-crf","18","-pix_fmt","yuv420p",
        "-profile:v","high","-level","4.2","-r",str(FPS),"-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",out],stdin=subprocess.PIPE)
    import itertools
    with Pool(4) as pool:
        for k,b in enumerate(pool.imap(work,itertools.islice(reader(),lim),chunksize=4)):
            enc.stdin.write(b)
            if k%300==0: print("frame",k,flush=True)
    enc.stdin.close(); enc.wait(); print("done",out)
