"""Empacotamento com PE fictício; sem executáveis ou mídias reais."""
import json
from pathlib import Path
import tempfile
import unittest

import package_release as release


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = self.root/release.SOURCE
        source.mkdir(parents=True)
        (source/'app.py').write_text('pass\n')
        blob = bytearray(256)
        blob[:2] = b'MZ'
        blob[60:64] = (64).to_bytes(4, 'little')
        blob[64:70] = b'PE\x00\x00\x64\x86'
        for name in release.ACTIVE:
            path = self.root/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(blob)
        self.manifest = dict(active_paths=release.ACTIVE,
                             inputs={'app.py': release.sha(source/'app.py')},
                             executable_sha256=release.sha(self.root/release.ACTIVE[0]))
        (self.root/'renamer final/build-manifest.json').write_text(json.dumps(self.manifest))
        (self.root/'renamer final/GUIA_DO_USUARIO.txt').write_text('Guia fictício')
        (self.root/'preferences.json').write_text('PRIVATE')
        self.output = self.root/'output'

    def test_package_contains_only_public_assets_and_roundtrips(self):
        release.package(self.root, self.output, 'a'*40)
        self.assertEqual(set(p.name for p in self.output.iterdir()),
                         set(release.ASSETS) | {'SHA256SUMS.txt', 'release-notes.md'})
        release.verify_assets(self.output)
        manifest = json.loads((self.output/'build-manifest.json').read_text())
        self.assertEqual(manifest['source_commit'], 'a'*40)
        self.assertNotIn('PRIVATE', (self.output/'release-notes.md').read_text())

    def test_changed_source_or_executable_blocks_before_output(self):
        for target in (self.root/release.SOURCE/'app.py', self.root/release.ACTIVE[1]):
            before = target.read_bytes()
            target.write_bytes(b'CHANGED')
            with self.assertRaises(ValueError):
                release.package(self.root, self.output, 'a'*40)
            self.assertFalse(self.output.exists())
            target.write_bytes(before)

    def test_download_corruption_is_detected(self):
        release.package(self.root, self.output, 'a'*40)
        (self.output/'MediaRenamer.exe').write_bytes(b'CORRUPTED')
        with self.assertRaisesRegex(ValueError, 'Hash divergente'):
            release.verify_assets(self.output)

    def test_existing_output_is_not_overwritten(self):
        self.output.mkdir()
        (self.output/'keep.txt').write_text('keep')
        with self.assertRaises(FileExistsError):
            release.package(self.root, self.output, 'a'*40)
        self.assertEqual((self.output/'keep.txt').read_text(), 'keep')


if __name__ == '__main__':
    unittest.main()
