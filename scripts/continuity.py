"""Continuidade local do mrenamer (Python 3.10+, sem dependências externas)."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINTS = ROOT / '.checkpoints'
EXCLUDED = {'.git', '.checkpoints', '.venv', 'venv', '__pycache__', 'build',
            'backups', 'node_modules', '.pytest_cache', '.ruff_cache'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def files():
    for directory, folders, names in os.walk(ROOT, followlinks=False):
        folders[:] = sorted(n for n in folders if n not in EXCLUDED
                            and not (Path(directory) / n).is_symlink())
        for name in sorted(names):
            path = Path(directory) / name
            if path.is_symlink() or not path.is_file():
                continue
            if name.startswith('.env') and name != '.env.example':
                continue
            if name.endswith(('.pyc', ':Zone.Identifier')):
                continue
            yield path


def verify(folder):
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    with tempfile.TemporaryDirectory(prefix='mrenamer-restore-') as temp:
        target = Path(temp)
        with zipfile.ZipFile(folder / 'source.zip') as archive:
            names = archive.namelist()
            if len(names) != len(manifest) or set(names) != set(manifest):
                raise ValueError('Inventário divergente')
            for name in names:
                if '\\' in name or not (target / name).resolve().is_relative_to(target):
                    raise ValueError('Caminho inválido no checkpoint')
            archive.extractall(target)
        for name, expected in manifest.items():
            if digest((target / name).read_bytes()) != expected:
                raise ValueError(f'Hash divergente: {name}')
    return len(manifest)


def checkpoint():
    CHECKPOINTS.mkdir(mode=0o700, exist_ok=True)
    name = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    pending = CHECKPOINTS / ('.pending-' + name)
    pending.mkdir(mode=0o700)
    manifest = {}
    with zipfile.ZipFile(pending / 'source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files():
            relative = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()
            archive.writestr(relative, data)
            manifest[relative] = digest(data)
    (pending / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    for path in pending.iterdir():
        path.chmod(0o600)
    count = verify(pending)
    pending.rename(CHECKPOINTS / name)
    pointer = CHECKPOINTS / ('.latest-' + name)
    pointer.write_text(json.dumps({'checkpoint': name}) + '\n', encoding='utf-8')
    pointer.chmod(0o600)
    pointer.replace(CHECKPOINTS / 'latest.json')
    print(f'Checkpoint restaurado e verificado: {count} arquivos; {name}')


def latest():
    name = json.loads((CHECKPOINTS / 'latest.json').read_text(encoding='utf-8'))['checkpoint']
    if not name or Path(name).name != name or name in {'.', '..'} or '\\' in name:
        raise ValueError('Identificador inválido')
    return CHECKPOINTS / name


def resume():
    print(f'Projeto: {ROOT}')
    for module in ('tkinter', 'tkinterdnd2', 'PyInstaller'):
        print(f'{module}: {"presente" if importlib.util.find_spec(module) else "ausente"}')
    print('Build .exe exige Python Windows; presença do módulo não valida a GUI.')
    if (CHECKPOINTS / 'latest.json').exists():
        print(f'Último checkpoint: {latest().name}')
    else:
        print('Último checkpoint: ausente')
    if (ROOT / '.git').exists():
        result = subprocess.run(['git', 'status', '--short'], cwd=ROOT, capture_output=True, text=True, check=True)
        print(result.stdout.strip() or 'Git sem alterações')
    else:
        print('Git local ainda não inicializado')
    print('Leia docs/CURRENT_STATE.md e docs/PROJECT_MEMORY.md.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('retomar', 'encerrar', 'verificar'))
    action = parser.parse_args().action
    if action == 'encerrar':
        checkpoint()
    elif action == 'verificar':
        print(f'Restauração temporária verificada: {verify(latest())} arquivos')
    else:
        resume()


if __name__ == '__main__':
    main()
