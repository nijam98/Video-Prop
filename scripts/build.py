import sys
src = open(sys.argv[1]).read()
head, body = src.split("<!--BODY-->", 1)
out = ('<!doctype html>\n<html lang="ms">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
       + head.strip() + '\n</head>\n<body>\n' + body.strip() + '\n</body>\n</html>\n')
open(sys.argv[2], "w").write(out)
