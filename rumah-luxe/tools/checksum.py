"""Print error/warning findings from the newest saved check report."""
import json, glob, os, sys
f = max(glob.glob('.hyperframes/artifacts/checks/*.json'), key=os.path.getmtime); d = json.load(open(f))
lv = sys.argv[1:] or ['error', 'warning']
for sec, v in d.items():
    if isinstance(v, dict) and 'findings' in v:
        for x in v['findings']:
            if x.get('severity') in lv:
                print(sec, x.get('severity'), x.get('code'), '|', str(x.get('text', ''))[:40], '|', (x.get('message') or '')[:170], '| t=', x.get('time'))
