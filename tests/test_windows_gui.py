"""Integração Tk/Windows em arquivos e preferências temporários."""
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'renamer' / 'Renomeador_de_Midia_Projeto'))
import media_renamer as gui


@unittest.skipUnless(os.name == 'nt', 'Exige GUI Windows')
class WindowsGuiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='mrenamer-gui-')
        self.folder = Path(self.temp.name) / 'media'
        self.folder.mkdir()
        (self.folder/'original.jpg').write_bytes(b'PHOTO')
        (self.folder/'video.mp4').write_bytes(b'VIDEO')
        self.config = Path(self.temp.name)/'preferences.json'
        self.patches = [patch.object(gui, 'CONFIG_PATH', self.config),
                        patch.object(gui.messagebox, 'askyesno', return_value=True),
                        patch.object(gui.messagebox, 'showinfo'),
                        patch.object(gui.messagebox, 'showwarning'),
                        patch.object(gui.messagebox, 'showerror')]
        self.mocks = [p.start() for p in self.patches]
        self.errors = []
        self.root = gui.TkinterDnD.Tk()
        self.root.withdraw()
        self.root.report_callback_exception = lambda *args: self.errors.append(args)
        self.app = gui.MediaRenamer(self.root)
        self.app.folder.set(str(self.folder))
        self.app.load_files()
        self.pump()

    def pump(self):
        for _ in range(3):
            self.root.update()
            time.sleep(.01)

    def tearDown(self):
        self.app.close_application()
        for p in reversed(self.patches):
            p.stop()
        self.temp.cleanup()
        self.assertEqual(self.errors, [])

    def test_pattern_rename_and_undo_preserve_bytes(self):
        self.app.base_name.set('Viagem')
        self.app.rename_files(); self.pump()
        self.assertEqual((self.folder/'Viagem_001.jpg').read_bytes(), b'PHOTO')
        self.assertEqual((self.folder/'Viagem_002.mp4').read_bytes(), b'VIDEO')
        self.app.undo_last_rename(); self.pump()
        self.assertEqual((self.folder/'original.jpg').read_bytes(), b'PHOTO')
        self.assertEqual((self.folder/'video.mp4').read_bytes(), b'VIDEO')
        self.mocks[-1].assert_not_called()

    def test_replacement_preview_matches_operation(self):
        self.app.preview_mode.set('Substituição')
        self.app.replace_text.set('original'); self.app.replace_with.set('nova')
        self.app.refresh_preview(); self.pump()
        self.assertEqual(self.app.tree.set('0', 'new'), 'nova.jpg')
        self.app.replace_selected_names(); self.pump()
        self.assertEqual((self.folder/'nova.jpg').read_bytes(), b'PHOTO')
        self.app.undo_last_rename(); self.pump()
        self.assertTrue((self.folder/'original.jpg').exists())
        self.mocks[-1].assert_not_called()

    def test_invalid_input_is_visible_and_blocks_operation(self):
        self.app.digits.set(''); self.pump()
        self.assertIn('inteiro', self.app.status.cget('text'))
        self.app.rename_files()
        self.mocks[-1].assert_called_once()
        self.assertEqual(len(list(self.folder.iterdir())), 2)
        self.app.digits.set('3.5'); self.pump()
        self.assertIn('inteiro', self.app.status.cget('text'))
        self.app.digits.set(3); self.pump()

    def test_search_selection_sort_theme_settings_and_drop(self):
        self.app.search_text.set('original'); self.pump()
        self.assertEqual(len(self.app.files), 1)
        self.app.search_text.set(''); self.pump()
        self.assertEqual(len(self.app.selected), 2)
        self.app.sort_mode.set('Tamanho'); self.app.apply_sort(); self.pump()
        self.app.theme_mode.set('Escuro'); self.app.apply_theme()
        self.app.open_settings(); self.pump()
        for child in self.root.winfo_children():
            if isinstance(child, gui.tk.Toplevel):
                child.destroy()
        self.app.on_drop(type('Drop', (), {'data': '{' + str(self.folder/'original.jpg') + '}'})())
        self.pump()
        self.assertEqual(self.app.selected, {self.folder/'original.jpg'})
        self.assertTrue(hasattr(self.root, 'drop_target_register'))

    def test_windows_file_lock_restores_previous_moves(self):
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        create = kernel.CreateFileW
        create.argtypes = (wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                           wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE)
        create.restype = wintypes.HANDLE
        kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
        handle = create(str(self.folder/'video.mp4'), 0x80000000, 1, None, 3, 0x80, None)
        self.assertNotEqual(handle, wintypes.HANDLE(-1).value)
        try:
            self.app.rename_files(); self.pump()
            self.assertEqual((self.folder/'original.jpg').read_bytes(), b'PHOTO')
            self.assertEqual((self.folder/'video.mp4').read_bytes(), b'VIDEO')
            self.assertEqual(self.app.undo_stack, [])
            self.mocks[-1].assert_called_once()
            self.assertIn('restaurados', self.mocks[-1].call_args.args[1])
            self.assertEqual(len(list(self.folder.iterdir())), 2)
        finally:
            kernel.CloseHandle(handle)

    def test_undo_cycle_uses_same_transaction(self):
        a = self.folder/'original.jpg'; b = self.folder/'second.jpg'
        b.write_bytes(b'SECOND')
        operations = [(a, b), (b, a)]
        self.app.rename_operations(operations)
        self.app.undo_stack.append({'operations': operations})
        self.app.undo_last_rename(); self.pump()
        self.assertEqual(a.read_bytes(), b'PHOTO')
        self.assertEqual(b.read_bytes(), b'SECOND')
        self.mocks[-1].assert_not_called()

    def test_background_monitor_discards_results_after_folder_change(self):
        from unittest.mock import Mock
        context = (str(self.folder), False, 'Todos', '', self.app._scan_generation)
        self.app._scan_results.put((context, [], None))
        self.app._scan_running = True
        self.app._scan_generation += 1
        self.root.after_cancel(self.app._watch_job)
        with patch.object(self.app, 'load_files') as load:
            self.app._poll_folder()
            load.assert_not_called()

    def test_tcl_drop_multiple_unicode_spaces_and_mixed_items(self):
        paths = [self.folder / 'ação {família}.jpg', self.folder / 'vídeo férias.mp4']
        for p in paths:
            p.write_bytes(b'FAKE')
        # Serialização real de uma lista Tcl, como o backend TkDnD entrega.
        data = self.root.tk.call('format', '%s', self.root.tk.call('list', *(str(p) for p in paths)))
        self.app.on_drop(type('Drop', (), {'data': data})())
        self.pump()
        self.assertEqual(self.app.selected, set(paths))
        before = self.app.folder.get()
        self.app.handle_dropped_paths([str(self.folder), str(paths[0])])
        self.mocks[-2].assert_called_once()
        self.assertEqual(self.app.folder.get(), before)
        other = Path(self.temp.name) / 'other'
        other.mkdir()
        p = other / 'photo.jpg'
        p.write_bytes(b'FAKE')
        self.app.handle_dropped_paths([str(paths[0]), str(p)])
        self.assertEqual(self.app.folder.get(), before)
        self.assertEqual(self.mocks[-2].call_count, 2)

    def test_assisted_recovery_preview_cancel_then_confirm(self):
        import rename_engine as engine
        source = self.folder / 'original.jpg'
        move = engine.move_no_replace
        calls = 0
        def block_after_first(a, b):
            nonlocal calls
            calls += 1
            if calls > 1:
                raise PermissionError('lock')
            move(a, b)
        with patch.object(engine, 'move_no_replace', side_effect=block_after_first):
            with self.assertRaises(engine.RenameTransactionError) as caught:
                engine.rename_batch([(source, source.with_name('changed.jpg'))])
        journal = caught.exception.journal
        with patch.object(gui.filedialog, 'askopenfilename', return_value=str(journal)):
            self.mocks[1].return_value = False
            self.app.recover_interrupted_batch()
            self.assertTrue(journal.exists())
            self.assertFalse(source.exists())
            self.mocks[1].return_value = True
            self.app.recover_interrupted_batch()
        self.assertEqual(source.read_bytes(), b'PHOTO')
        self.assertFalse(journal.exists())
        self.mocks[-1].assert_not_called()

    def test_date_and_monitoring(self):
        self.app.use_date.set(True); self.app.refresh_preview()
        self.assertRegex(self.app.tree.set('0', 'new'), r'Arquivo_\d{4}-\d{2}-\d{2}_001.jpg')
        p = self.folder/'new.jpg'; p.write_bytes(b'NEW')
        self.app.load_files(auto=True); self.assertNotIn(p, self.app.files)
        self.app.load_files(auto=True); self.assertIn(p, self.app.files)
        (self.folder/'original.jpg').write_bytes(b'CHANGED')
        self.app.load_files(auto=True); self.pump()
        self.assertEqual(len(self.app.files), 3)


@unittest.skipUnless(os.name == 'nt', 'Exige GUI Windows')
class WindowsScalingTests(unittest.TestCase):
    def test_startup_and_row_font_at_100_150_200_percent(self):
        for percent in (100, 150, 200):
            with self.subTest(percent=percent), tempfile.TemporaryDirectory() as temp:
                with patch.object(gui, 'CONFIG_PATH', Path(temp) / 'preferences.json'):
                    root = gui.TkinterDnD.Tk()
                    root.withdraw()
                    root.tk.call('tk', 'scaling', (96 / 72) * percent / 100)
                    app = gui.MediaRenamer(root)
                    try:
                        root.update_idletasks()
                        font = gui.tkfont.Font(root, font=('Segoe UI', 10))
                        rowheight = int(app.style.lookup('Treeview', 'rowheight'))
                        self.assertGreaterEqual(rowheight, font.metrics('linespace') + 10)
                        self.assertLessEqual(root.minsize()[0], root.winfo_screenwidth())
                        self.assertLessEqual(root.minsize()[1], root.winfo_screenheight())
                        app.theme_mode.set('Escuro')
                        app.apply_theme()
                        self.assertEqual(rowheight, int(app.style.lookup('Treeview', 'rowheight')))
                    finally:
                        app.close_application()


if __name__ == '__main__':
    unittest.main()
