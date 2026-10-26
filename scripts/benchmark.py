"""Benchmark local, apenas arquivos fictícios temporários; saída JSON."""
import argparse
import json
import os
from pathlib import Path
import platform
import sys
import tempfile
from time import perf_counter
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'renamer' / 'Renomeador_de_Midia_Projeto'
sys.path.insert(0, str(SOURCE))
import media_renamer as gui
import rename_engine as engine


def measure(count, with_gui):
    with tempfile.TemporaryDirectory(prefix='mrenamer-benchmark-') as temporary:
        folder = Path(temporary)
        files = [folder / f'foto_{i:06}.jpg' for i in range(count)]
        for p in files:
            p.write_bytes(b'FAKE PHOTO')
        result = {'files': count}
        def timed(name, operation):
            start = perf_counter()
            value = operation()
            result[name] = round(perf_counter() - start, 4)
            return value
        timed('scan_seconds', lambda: gui.MediaRenamer._scan_folder(str(folder), False))
        if with_gui:
            with patch.object(gui, 'CONFIG_PATH', folder / 'preferences.json'):
                root = gui.TkinterDnD.Tk()
                root.withdraw()
                app = gui.MediaRenamer(root)
                try:
                    root.after_cancel(app._watch_job)
                    app.folder.set(str(folder))
                    timed('load_preview_seconds', app.load_files)
                    timed('preview_seconds', app.refresh_preview)
                    assert len(app.tree.get_children()) == count
                finally:
                    app.close_application()
        operations = [(p, p.with_name('renamed_' + p.name)) for p in files]
        timed('validate_seconds', lambda: engine.validate_operations(operations))
        timed('rename_seconds', lambda: engine.rename_batch(operations))
        timed('undo_seconds', lambda: engine.rename_batch([(b, a) for a, b in operations]))
        assert all(p.read_bytes() == b'FAKE PHOTO' for p in files)
        assert not list(folder.glob('.__renamer_*'))
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--counts', type=int, nargs='+', default=[1000, 10000])
    parser.add_argument('--gui', action='store_true')
    args = parser.parse_args()
    if any(n < 1 or n > 100000 for n in args.counts):
        parser.error('Use entre 1 e 100000 arquivos por medição.')
    print(json.dumps({'python': platform.python_version(), 'os': os.name,
                      'storage': 'temporary directory, warm cache, synthetic 10-byte files',
                      'gui': args.gui, 'results': [measure(n, args.gui) for n in args.counts]}, indent=2))


if __name__ == '__main__':
    main()
