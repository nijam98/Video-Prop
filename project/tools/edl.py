import json
FPS=30
fr=lambda x: round(x*FPS)/FPS
SEGS=[(8.31,12.90),(0.30,2.50),(3.57,5.45),(12.90,13.80),(14.40,17.66),(18.55,20.73)]
W=json.load(open("aligned.json"))
out=[];t=0.0;edl=[]
for i,(a,b) in enumerate(SEGS):
    d=fr(b-a); edl.append({"i":i+1,"src":a,"start":round(t,4),"dur":d})
    for k,w in enumerate(W):
        if w["s"]>=a-0.02 and w["e"]<=b+0.05:
            out.append({"k":k,"w":w["w"],"s":round(w["s"]-a+t,3),"e":round(min(w["e"],b)-a+t,3),"seg":i+1})
    t=round(t+d,4)
json.dump({"edl":edl,"total":t,"words":out},open("edl.json","w"),indent=1)
for e in edl: print(e)
print("total",t)
for w in out: print(w["seg"],w["k"],f'{w["s"]:.2f}-{w["e"]:.2f}',w["w"])
