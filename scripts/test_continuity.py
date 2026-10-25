"""Testes de recuperação em pastas temporárias; nunca usam os arquivos reais."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

import continuity


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.old = continuity.ROOT, continuity.CHECKPOINTS
        continuity.ROOT = Path(self.temp.name)
        continuity.CHECKPOINTS = continuity.ROOT / '.checkpoints'

    def tearDown(self):
        continuity.ROOT, continuity.CHECKPOINTS = self.old
        self.temp.cleanup()

    def checkpoint(self):
        with contextlib.redirect_stdout(io.StringIO()):
            continuity.checkpoint()
        return continuity.latest()

    def test_restore_preserves_source_and_distribution_excludes_private_files(self):
        root = continuity.ROOT
        for name in ('app.py', 'renamer final/MediaRenamer.exe', 'backups/old.exe',
                     'build/temp', '.env', '.env.example', '.git/config', 'x.pyc'):
            file = root / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(b'original')
        folder = self.checkpoint()
        self.assertEqual(continuity.verify(folder), 3)
        (root / 'app.py').write_bytes(b'changed')
        self.assertEqual(continuity.verify(folder), 3)
        self.assertEqual((root / 'app.py').read_bytes(), b'changed')

    def test_corruption_is_detected(self):
        (continuity.ROOT / 'app.py').write_text('original')
        folder = self.checkpoint()
        with zipfile.ZipFile(folder / 'source.zip', 'w') as archive:
            archive.writestr('app.py', b'corrupt')
        with self.assertRaisesRegex(ValueError, 'Hash divergente'):
            continuity.verify(folder)

    def test_path_traversal_is_rejected(self):
        folder = continuity.ROOT / 'bad'
        folder.mkdir()
        name = '../escape'
        (folder / 'manifest.json').write_text(json.dumps({name: continuity.digest(b'x')}))
        with zipfile.ZipFile(folder / 'source.zip', 'w') as archive:
            archive.writestr(name, b'x')
        with self.assertRaisesRegex(ValueError, 'Caminho inválido'):
            continuity.verify(folder)
        self.assertFalse((continuity.ROOT / 'escape').exists())


if __name__ == '__main__':
    unittest.main()
