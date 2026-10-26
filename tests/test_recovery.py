"""Interrupção abrupta em processo isolado e recuperação com dados fictícios."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'renamer' / 'Renomeador_de_Midia_Projeto'
sys.path.insert(0, str(SOURCE))
import rename_engine as engine


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.a = self.folder / 'a.jpg'
        self.b = self.folder / 'b.jpg'
        self.a.write_bytes(b'AAA')
        self.b.write_bytes(b'BBB')

    def interrupt(self, stage=1):
        code = '''
import os, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import rename_engine as e
folder = Path(sys.argv[2])
move = e.move_no_replace
calls = 0
def interrupted(a, b):
    global calls
    move(a, b)
    calls += 1
    if calls == int(sys.argv[3]):
        os._exit(73)
e.move_no_replace = interrupted
e.rename_batch([(folder/'a.jpg', folder/'b.jpg'), (folder/'b.jpg', folder/'a.jpg')])
'''
        result = subprocess.run([sys.executable, '-c', code, str(SOURCE), str(self.folder), str(stage)])
        self.assertEqual(result.returncode, 73)
        return next(self.folder.glob('.__renamer_recovery_*.json'))

    def test_abrupt_exit_at_each_move_recovers_cycle(self):
        for stage in range(1, 5):
            with self.subTest(stage=stage):
                journal = self.interrupt(stage)
                plan = engine.recovery_plan(journal)
                engine.recover_journal(journal, plan)
                self.assertEqual(self.a.read_bytes(), b'AAA')
                self.assertEqual(self.b.read_bytes(), b'BBB')
                self.assertEqual(sorted(p.name for p in self.folder.iterdir()), ['a.jpg', 'b.jpg'])

    @unittest.skipUnless(os.name == 'nt', 'Grafia de caminhos case-insensitive no Windows')
    def test_case_only_recovery_uses_actual_directory_spelling(self):
        # Mapa residual após sucesso permite restauração explícita do nome.
        with patch.object(Path, 'unlink', side_effect=PermissionError('keep journal')):
            engine.rename_batch([(self.a, self.a.with_name('A.jpg'))])
        journal = next(self.folder.glob('.__renamer_recovery_*.json'))
        plan = engine.recovery_plan(journal)
        self.assertEqual(plan[0][0].name, 'A.jpg')
        engine.recover_journal(journal, plan)
        self.assertIn('a.jpg', [p.name for p in self.folder.iterdir()])

    def test_external_destination_blocks_without_moves(self):
        journal = self.interrupt()
        self.a.write_bytes(b'EXTERNAL')
        with self.assertRaises(FileExistsError):
            engine.recovery_plan(journal)
        self.assertEqual(self.a.read_bytes(), b'EXTERNAL')
        self.assertTrue(journal.exists())

    def test_changed_or_missing_file_blocks_without_moves(self):
        journal = self.interrupt()
        temporary = next(self.folder.glob('.__renamer_tmp_*'))
        temporary.write_bytes(b'CHANGED')
        with self.assertRaisesRegex(ValueError, 'alterado'):
            engine.recovery_plan(journal)
        temporary.unlink()
        with self.assertRaisesRegex(ValueError, 'ausente'):
            engine.recovery_plan(journal)

    def test_changed_preview_is_revalidated(self):
        journal = self.interrupt()
        plan = engine.recovery_plan(journal)
        self.a.write_bytes(b'EXTERNAL')
        with self.assertRaises(FileExistsError):
            engine.recover_journal(journal, plan)
        self.assertTrue(journal.exists())

    def test_invalid_old_outside_and_duplicate_maps_rejected(self):
        journal = self.interrupt()
        data = json.loads(journal.read_text(encoding='utf-8'))
        import copy
        variants = [[], {'version': 1}, {'version': 2, 'operations': []}]
        outside = copy.deepcopy(data)
        outside['operations'][0]['original'] = str(self.folder.parent/'outside.jpg')
        variants.append(outside)
        duplicate = copy.deepcopy(data)
        duplicate['operations'].append(duplicate['operations'][0])
        variants.append(duplicate)
        for variant in variants:
            journal.write_text(json.dumps(variant), encoding='utf-8')
            with self.subTest(variant=variant), self.assertRaises(ValueError):
                engine.recovery_plan(journal)
        self.assertEqual(self.b.read_bytes(), b'BBB')

    def test_sibling_folders_use_common_parent_map(self):
        sub = self.folder / 'sub'
        sub.mkdir()
        c = sub / 'c.jpg'
        c.write_bytes(b'CCC')
        move = engine.move_no_replace
        calls = 0
        def block(a, b):
            nonlocal calls
            calls += 1
            if calls > 1:
                raise PermissionError('lock')
            move(a, b)
        with patch.object(engine, 'move_no_replace', side_effect=block):
            with self.assertRaises(engine.RenameTransactionError) as caught:
                engine.rename_batch([(c, sub/'d.jpg'), (self.a, self.folder/'x.jpg')])
        journal = caught.exception.journal
        self.assertEqual(journal.parent, self.folder)
        engine.recover_journal(journal, engine.recovery_plan(journal))
        self.assertEqual(c.read_bytes(), b'CCC')
        self.assertEqual(self.a.read_bytes(), b'AAA')

    def test_symlink_candidate_rejected(self):
        journal = self.interrupt()
        temporary = next(self.folder.glob('.__renamer_tmp_*'))
        try:
            self.a.symlink_to(temporary)
        except OSError:
            self.skipTest('Sistema não permite symlink neste ambiente')
        with self.assertRaisesRegex(ValueError, 'link'):
            engine.recovery_plan(journal)
        self.assertTrue(journal.exists())
        self.a.unlink()

    def test_failure_during_recovery_keeps_original_map(self):
        journal = self.interrupt()
        plan = engine.recovery_plan(journal)
        with patch.object(engine, 'move_no_replace', side_effect=PermissionError('lock')):
            with self.assertRaises(engine.RenameTransactionError):
                engine.recover_journal(journal, plan)
        self.assertTrue(journal.exists())
        engine.recover_journal(journal, engine.recovery_plan(journal))
        self.assertEqual(self.a.read_bytes(), b'AAA')


if __name__ == '__main__':
    unittest.main()
