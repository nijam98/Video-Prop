"""Find the presenter's head in every 3rd frame (10 fps) -> JSON list of {t, top, x, ok}."""
import sys, json, cv2
import mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision

video, det_model, pose_model, out = sys.argv[1:5]
det = vision.ObjectDetector.create_from_options(vision.ObjectDetectorOptions(
    base_options=mpt.BaseOptions(model_asset_path=det_model), score_threshold=0.35, category_allowlist=["person"], max_results=3))
pose = vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(
    base_options=mpt.BaseOptions(model_asset_path=pose_model), num_poses=1, min_pose_detection_confidence=0.4))
cap = cv2.VideoCapture(video)
fps = cap.get(cv2.CAP_PROP_FPS)
res, i = [], 0
while True:
    ok, frame = cap.read()
    if not ok: break
    if i % 3 == 0:
        t = i / fps
        h, w = frame.shape[:2]
        img = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        dets = det.detect(img).detections
        rec = {"t": round(t, 3), "ok": False}
        if dets:
            b = max(dets, key=lambda d: d.bounding_box.width * d.bounding_box.height).bounding_box
            if b.height > 0.2 * h:
                rec.update(ok=True, top=b.origin_y, x=b.origin_x + b.width / 2, bh=b.height)
        p = pose.detect(img).pose_landmarks
        if p:
            lm = p[0]
            head = [lm[k] for k in range(0, 11) if lm[k].visibility > 0.3]
            if head:
                rec["hx"] = sum(l.x for l in head) / len(head) * w
                rec["hy"] = min(l.y for l in head) * h
        res.append(rec)
        if len(res) % 100 == 0: print(t, rec, flush=True)
    i += 1
json.dump(res, open(out, "w"))
print("frames", len(res))
