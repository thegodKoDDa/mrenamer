"""Regressões com arquivos fictícios; nenhuma preferência ou mídia real é usada."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

SOURCE = Path(__file__).resolve().parents[1] / 'renamer' / 'Renomeador_de_Midia_Projeto'
sys.path.insert(0, str(SOURCE))
import rename_engine as engine
import media_renamer as gui


class FileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def file(self, name, data=None):
        p = self.root / name
        p.write_bytes(data if data is not None else name.encode())
        return p

    def contents(self):
        return {p.name: p.read_bytes() for p in self.root.iterdir()}

    def test_cycles_and_reverse_preserve_contents(self):
        a, b, c = (self.file(name) for name in ('a.jpg', 'b.jpg', 'c.jpg'))
        before = self.contents()
        operations = [(a, b), (b, c), (c, a)]
        engine.rename_batch(operations)
        self.assertEqual(b.read_bytes(), b'a.jpg')
        engine.rename_batch([(new, old) for old, new in operations])
        self.assertEqual(self.contents(), before)

    def test_failure_at_every_stage_rolls_back_cycle(self):
        for fail_at in range(1, 7):
            with self.subTest(fail_at=fail_at):
                for p in self.root.iterdir():
                    p.unlink()
                a, b, c = (self.file(name) for name in ('a.jpg', 'b.jpg', 'c.jpg'))
                before = self.contents()
                move = engine.move_no_replace
                calls = 0

                def fail_once(old, new):
                    nonlocal calls
                    calls += 1
                    if calls == fail_at:
                        raise PermissionError('Falha simulada')
                    move(old, new)

                with patch.object(engine, 'move_no_replace', side_effect=fail_once):
                    with self.assertRaises(engine.RenameTransactionError) as caught:
                        engine.rename_batch([(a, b), (b, c), (c, a)])
                self.assertTrue(caught.exception.rolled_back)
                self.assertEqual(caught.exception.completed, max(0, fail_at - 4))
                self.assertEqual(self.contents(), before)

    def test_failed_rollback_keeps_journal_and_actual_locations(self):
        a, b = self.file('a.jpg'), self.file('b.jpg')
        move = engine.move_no_replace
        calls = 0

        def block(old, new):
            nonlocal calls
            calls += 1
            if calls >= 2:
                raise PermissionError('Bloqueado')
            move(old, new)

        with patch.object(engine, 'move_no_replace', side_effect=block):
            with self.assertRaises(engine.RenameTransactionError) as caught:
                engine.rename_batch([(a, a.with_name('x.jpg')), (b, b.with_name('y.jpg'))])
        error = caught.exception
        self.assertFalse(error.rolled_back)
        record = json.loads(error.journal.read_text(encoding='utf-8'))
        self.assertEqual(len(record['operations']), 2)
        self.assertIn(str(error.journal), str(error))
        self.assertEqual(Path(record['operations'][0]['temporary']).read_bytes(), b'a.jpg')
        self.assertEqual(b.read_bytes(), b'b.jpg')

    def test_destination_created_during_batch_is_never_overwritten(self):
        a = self.file('a.jpg')
        target = a.with_name('x.jpg')
        move = engine.move_no_replace

        def race(old, new):
            if new == target:
                target.write_bytes(b'EXTERNAL')
            move(old, new)

        with patch.object(engine, 'move_no_replace', side_effect=race):
            with self.assertRaises(engine.RenameTransactionError):
                engine.rename_batch([(a, target)])
        self.assertEqual(a.read_bytes(), b'a.jpg')
        self.assertEqual(target.read_bytes(), b'EXTERNAL')

    def test_duplicate_destinations_case_insensitive_rejected_before_moving(self):
        a, b = self.file('a.jpg'), self.file('b.jpg')
        before = self.contents()
        with self.assertRaisesRegex(ValueError, 'duplicados'):
            engine.rename_batch([(a, a.with_name('x.jpg')), (b, b.with_name('X.jpg'))])
        self.assertEqual(self.contents(), before)

    def test_replacement_can_target_another_selected_source(self):
        a, b = self.file('aaa.jpg'), self.file('aa.jpg')
        operations = [(p, p.with_name(engine.replace_stem(p, 'aa', 'a'))) for p in (a, b)]
        engine.rename_batch(operations)
        self.assertEqual((self.root/'aa.jpg').read_bytes(), b'aaa.jpg')
        self.assertEqual((self.root/'a.jpg').read_bytes(), b'aa.jpg')

    def test_existing_destination_case_insensitive_rejected(self):
        a, b = self.file('a.jpg'), self.file('X.jpg')
        with self.assertRaises(FileExistsError):
            engine.rename_batch([(a, b.with_name('x.jpg'))])
        self.assertTrue(a.exists())

    def test_extension_change_rejected(self):
        a = self.file('a.jpg')
        with self.assertRaisesRegex(ValueError, 'extensão'):
            engine.rename_batch([(a, a.with_suffix('.png'))])

    def test_missing_source_and_repeated_source_rejected(self):
        a = self.file('a.jpg')
        for operations in ([(a.with_name('missing.jpg'), a)], [(a, a), (a, a)]):
            with self.assertRaises(ValueError):
                engine.rename_batch(operations)
        self.assertTrue(a.exists())

    def test_noop_is_not_recorded(self):
        a = self.file('a.jpg')
        self.assertEqual(engine.rename_batch([(a, a)]), [])
        self.assertEqual(len(self.contents()), 1)

    def test_case_only_rename_and_reverse(self):
        a = self.file('lower.jpg')
        upper = a.with_name('LOWER.jpg')
        engine.rename_batch([(a, upper)])
        self.assertEqual(upper.read_bytes(), b'lower.jpg')
        engine.rename_batch([(upper, a)])
        self.assertEqual(a.read_bytes(), b'lower.jpg')

    def test_journal_failure_prevents_any_move(self):
        a = self.file('a.jpg')
        with patch.object(engine.os, 'fsync', side_effect=PermissionError('Disco')):
            with self.assertRaises(PermissionError):
                engine.rename_batch([(a, a.with_name('x.jpg'))])
        self.assertEqual(a.read_bytes(), b'a.jpg')

    def test_symlink_rejected_when_supported(self):
        a = self.file('a.jpg')
        link = a.with_name('link.jpg')
        try:
            link.symlink_to(a)
        except OSError:
            self.skipTest('Sistema não permite symlink neste ambiente')
        with self.assertRaises(ValueError):
            engine.rename_batch([(link, link.with_name('x.jpg'))])


class NameTests(unittest.TestCase):
    def test_invalid_windows_names(self):
        for name in ('', '.', '..', 'CON.jpg', 'nul.txt', 'LPT1.jpeg', 'COM¹.txt',
                     'CONIN$.txt', 'CON .jpg', 'a/b.jpg', 'a\\b.jpg', 'a:b.jpg',
                     'a?.jpg', 'a\x00.jpg', 'a\n.jpg', 'a.jpg ', 'a.', 'a' * 256):
            with self.subTest(name=repr(name)), self.assertRaises(ValueError):
                engine.validate_name(name)

    def test_unicode_and_valid_names(self):
        for name in ('Viagem_001.JPG', 'Ação e família.jpg', 'auxiliar.txt', 'arquivo.tar.gz'):
            self.assertEqual(engine.validate_name(name), name)

    def test_replacement_does_not_change_extension(self):
        self.assertEqual(engine.replace_stem(Path('jpg_foto.jpg'), 'jpg', 'png'), 'png_foto.jpg')
        self.assertEqual(engine.replace_stem(Path('foto.JPG'), 'JPG', 'png'), 'foto.JPG')
        self.assertEqual(engine.replace_stem(Path('foto.tar.gz'), 'tar', 'zip'), 'foto.zip.gz')

    def test_replacement_invalid_or_empty_stem(self):
        for replacement in ('', '../bad', 'bad:', 'CON', 'bad.', ' '):
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                engine.replace_stem(Path('foto.jpg'), 'foto', replacement)


class GuiLogicTests(unittest.TestCase):
    def setUp(self):
        self.app = gui.MediaRenamer.__new__(gui.MediaRenamer)
        self.tcl = gui.tk.Tcl()
        for name, value in dict(base_name='Foto', separator='_', start_number='1', digits='3',
                                use_date=False, replace_text='jpg', replace_with='png',
                                preview_mode='Padrão', search_text='', folder='').items():
            setattr(self.app, name, gui.tk.StringVar(self.tcl, value=value)
                    if name != 'use_date' else gui.tk.BooleanVar(self.tcl, value=value))
        self.app.files = []
        self.app.selected = set()
        self.app.hidden_selected = set()
        self.app._pending_sizes = {}
        self.app._updating_tree = False

    def test_pattern_separate_from_replacement_preview(self):
        path = Path('jpg_original.jpg')
        self.assertEqual(self.app.make_new_name(0, path), 'Foto_001.jpg')
        self.app.preview_mode.set('Substituição')
        self.assertEqual(self.app._preview_name(0, path), 'png_original.jpg')

    def test_selected_index_controls_contiguous_numbering(self):
        self.assertEqual(self.app.make_new_name(2, Path('x.JPG')), 'Foto_003.JPG')

    def test_invalid_numeric_fields_raise_clear_validation(self):
        for name, invalid in (('digits', ''), ('digits', '0'), ('digits', '9'), ('digits', '3.5'),
                              ('start_number', '-1'), ('start_number', '1.5'), ('start_number', 'abc'),
                              ('start_number', '1000000')):
            var = getattr(self.app, name)
            original = var.get()
            var.set(invalid)
            with self.subTest(field=name, invalid=invalid), self.assertRaises(ValueError):
                self.app.make_new_name(0, Path('x.jpg'))
            var.set(original)

    def test_replacement_duplicate_rejected_in_ui_without_confirmation(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory)/'a-x.jpg', Path(directory)/'ax.jpg'
            a.write_bytes(b'A'); b.write_bytes(b'B')
            self.app.files = [a, b]; self.app.selected = {a, b}
            self.app.replace_text.set('-'); self.app.replace_with.set('')
            self.app.refresh_preview = Mock()
            with patch.object(gui.messagebox, 'showerror') as error, patch.object(gui.messagebox, 'askyesno') as confirm:
                self.app.replace_selected_names()
            error.assert_called_once(); confirm.assert_not_called()
            self.assertEqual(a.read_bytes(), b'A')

    def test_refresh_invalid_input_does_not_raise(self):
        self.app.digits.set('')
        self.app.tree = Mock()
        self.app.tree.get_children.return_value = []
        self.app.status = Mock(); self.app.selection_summary = Mock()
        self.app.example_label = Mock(); self.app.update_undo_button = Mock()
        self.app.refresh_preview()
        self.assertIn('inteiro', self.app.status.config.call_args.kwargs['text'])

    def test_programmatic_selection_event_does_not_refresh_again(self):
        p = Path('a.jpg')
        self.app.files = [p]; self.app.selected = {p}
        self.app.tree = Mock(); self.app.tree.selection.return_value = ['0']
        self.app.refresh_preview = Mock()
        self.app.on_tree_select()
        self.app.refresh_preview.assert_not_called()

    def test_stability_waits_for_second_matching_size(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)/'x.jpg'; p.write_bytes(b'A')
            self.assertFalse(self.app._file_is_stable(p, set()))
            p.write_bytes(b'AB')
            self.assertFalse(self.app._file_is_stable(p, set()))
            self.assertTrue(self.app._file_is_stable(p, set()))


if __name__ == '__main__':
    unittest.main()
