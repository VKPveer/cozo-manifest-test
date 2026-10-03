import argparse, json
from pathlib import Path
from jsonschema import Draft7Validator

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--manifest',default='project-manifest.json'); ap.add_argument('--schema',default='manifest-schema.json'); args=ap.parse_args()
    m=json.loads(Path(args.manifest).read_text(encoding='utf-8')); s=json.loads(Path(args.schema).read_text(encoding='utf-8')); errs=list(Draft7Validator(s).iter_errors(m))
    if errs:
        print('❌ Project Manifest is INVALID')
        for e in errs[:20]: print('-', '/'.join(map(str,e.path)) or '<root>', ':', e.message)
        raise SystemExit(1)
    print('✅ Project Manifest is VALID')
if __name__=='__main__': main()
