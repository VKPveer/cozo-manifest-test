import argparse
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone

DEFAULT_IGNORE = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build', '.idea', '.vscode', 'coverage', '.pytest_cache'}
DEFAULT_EXTENSIONS = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cs', '.cpp', '.c', '.h', '.hpp', '.go', '.rs', '.php', '.rb', '.sql', '.json', '.yaml', '.yml'}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load_config(config_path: str | None) -> dict:
    if not config_path:
        return {}
    p = Path(config_path)
    if not p.exists():
        return {}
    with p.open('r', encoding='utf-8') as f:
        return json.load(f)


def scan_repository(repo: Path, config: dict) -> list[dict]:
    ignore = set(config.get('ignore_folders', DEFAULT_IGNORE)) | DEFAULT_IGNORE
    supported = set(x.lower() for x in config.get('supported_extensions', DEFAULT_EXTENSIONS))
    files = []
    for root, directories, filenames in os.walk(repo):
        directories[:] = [d for d in directories if d not in ignore]
        for filename in filenames:
            p = Path(root) / filename
            ext = p.suffix.lower()
            if ext not in supported:
                continue
            try:
                stat = p.stat()
                rel = p.relative_to(repo).as_posix()
                files.append({
                    'path': rel,
                    'name': p.name,
                    'extension': ext,
                    'type': 'source',
                    'size': stat.st_size,
                    'hash': sha256_file(p),
                    'last_modified': datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                })
            except (OSError, PermissionError) as exc:
                files.append({'path': str(p), 'name': p.name, 'extension': ext, 'type': 'source', 'scan_error': str(exc)})
    files.sort(key=lambda x: x.get('path', ''))
    return files


def main():
    parser = argparse.ArgumentParser(description='Recursively inventory a real source repository.')
    parser.add_argument('--repo', required=True, help='Path to cloned/unzipped GitHub repository')
    parser.add_argument('--config', default=str(Path(__file__).with_name('config.json')))
    parser.add_argument('--output', default=str(Path(__file__).parent / 'output' / 'file_inventory.json'))
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        raise SystemExit(f'❌ Repository folder not found: {repo}')
    config = load_config(args.config)
    result = {'repository_root': str(repo), 'files': scan_repository(repo, config)}
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(f'✅ File inventory generated: {out}')
    print(f'Total files scanned: {len(result["files"])}')


if __name__ == '__main__':
    main()
