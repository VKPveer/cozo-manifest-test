import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from jsonschema import Draft7Validator


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--manifest',required=True); ap.add_argument('--schema',required=True); ap.add_argument('--output',default=str(Path(__file__).parent/'output'/'validation_report.json')); args=ap.parse_args()
    manifest=json.loads(Path(args.manifest).read_text(encoding='utf-8')); schema=json.loads(Path(args.schema).read_text(encoding='utf-8'))
    errors=sorted(Draft7Validator(schema).iter_errors(manifest), key=lambda e:list(e.path))
    report={'validation_time':datetime.now(timezone.utc).isoformat(),'manifest_file':str(Path(args.manifest).resolve()),'schema_file':str(Path(args.schema).resolve()),'status':'VALID' if not errors else 'INVALID','errors':[]}
    for e in errors:
        report['errors'].append({'path':'/'.join(str(x) for x in e.path),'message':e.message})
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,indent=2),encoding='utf-8')
    if errors:
        print('❌ PROJECT MANIFEST IS INVALID')
        for e in report['errors'][:20]: print(f"- {e['path'] or '<root>'}: {e['message']}")
        raise SystemExit(1)
    print('✅ PROJECT MANIFEST IS VALID')
    print(f'Validation report: {out}')
if __name__=='__main__': main()
