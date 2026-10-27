import cv2, json, sys
cap=cv2.VideoCapture(sys.argv[1]); fps=cap.get(5)
casc=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
prof=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_profileface.xml")
out=[];i=0
while True:
    ok,f=cap.read()
    if not ok: break
    if i%6==0:
        g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
        fs=list(casc.detectMultiScale(g,1.1,6,minSize=(40,40)))
        if not len(fs): fs=list(prof.detectMultiScale(g,1.1,5,minSize=(40,40)))
        best=max(fs,key=lambda r:r[2]*r[3]) if len(fs) else None
        out.append({"t":round(i/fps,2),"face":[int(v) for v in best] if best is not None else None})
    i+=1
json.dump(out,open(sys.argv[2],"w"))
for o in out: print(o["t"], o["face"])
