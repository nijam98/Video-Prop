"""Inline tools/common.css and tools/common.js into every scene between the COMMON markers.
usage: python3 tools/build.py"""
import glob, os, re
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
css = open(os.path.join(root, "tools/common.css")).read().strip()
js = open(os.path.join(root, "tools/common.js")).read().strip()
for f in sorted(glob.glob(os.path.join(root, "compositions/*.html"))):
    s = open(f).read()
    s = re.sub(r"/\* BEGIN COMMON \*/.*?/\* END COMMON \*/", lambda m: "/* BEGIN COMMON */\n" + css + "\n/* END COMMON */", s, flags=re.S)
    s = re.sub(r"// BEGIN COMMON.*?// END COMMON", lambda m: "// BEGIN COMMON\n" + js + "\n// END COMMON", s, flags=re.S)
    open(f, "w").write(s); print("built", os.path.basename(f))
