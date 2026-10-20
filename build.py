"""Build index.html (installable app for GitHub Pages) and the Claude artifact copy from src/app.html."""
import re, sys, pathlib

root = pathlib.Path(__file__).parent
body = (root / "src/app.html").read_text()
avatar = (root / "src/avatar.b64").read_text().strip()
body = body.replace("__AVATAR__", "data:image/jpeg;base64," + avatar)

pwa_head = """<meta name="theme-color" content="#241c17">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="NAZ Kelayakan">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<link rel="icon" type="image/png" href="icons/icon-192.png">
"""
# Split head-ish part (title, meta, links, style) from page markup
i = body.index("</style>") + len("</style>")
head, markup = body[:i], body[i:]
full = ('<!doctype html>\n<html lang="ms">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + head.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '<meta name="claude:viewport-fit-sides" content="cover">\n' + pwa_head, 1)
        + "\n</head>\n<body>" + markup + "</body>\n</html>\n")
(root / "index.html").write_text(full)
if len(sys.argv) > 1:
    pathlib.Path(sys.argv[1]).write_text(body)
print("built", len(full))
