import argparse
import json
from pathlib import Path

LANGUAGE_MAP = {
    '.py': 'Python', '.js': 'JavaScript', '.jsx': 'JavaScript', '.ts': 'TypeScript', '.tsx': 'TypeScript',
    '.java': 'Java', '.cs': 'CSharp', '.cpp': 'C++', '.c': 'C', '.h': 'C/C++ Header', '.hpp': 'C++ Header',
    '.go': 'Go', '.rs': 'Rust', '.php': 'PHP', '.rb': 'Ruby', '.sql': 'SQL', '.json': 'JSON', '.yaml': 'YAML', '.yml': 'YAML'
}

def detect_language(path: str) -> str:
    return LANGUAGE_MAP.get(Path(path).suffix.lower(), 'Unknown')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', default=str(Path(__file__).with_name('language_updated_inventory.json')))
    args = parser.parse_args()
    data = json.loads(Path(args.input).read_text(encoding='utf-8'))
    for item in data.get('files', []):
        item['language'] = detect_language(item.get('path', ''))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(data, indent=2), encoding='utf-8')
    print(f'✅ Language detection completed: {args.output}')

if __name__ == '__main__':
    main()
