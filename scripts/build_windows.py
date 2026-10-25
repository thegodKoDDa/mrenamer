"""Gera, abre e distribui o .exe no Windows, com backups e proveniência."""
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'renamer' / 'Renomeador_de_Midia_Projeto'
ACTIVE = [ROOT / 'renamer final' / 'MediaRenamer.exe', SOURCE / 'dist' / 'MediaRenamer.exe']
PACKAGES = ('PyInstaller', 'tkinterdnd2', 'altgraph', 'packaging',
            'pyinstaller-hooks-contrib', 'pefile', 'pywin32-ctypes', 'setuptools')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def smoke(executable, profile):
    # Abre somente a build temporária e fecha sua própria janela normalmente.
    # USERPROFILE temporário impede gravação nas preferências reais.
    env = {**os.environ, 'USERPROFILE': str(profile), 'MRENAMER_SMOKE_EXE': str(executable)}
    code = r'''
$ErrorActionPreference = 'Stop'
$exe = $env:MRENAMER_SMOKE_EXE
$started = Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -PassThru
$window = $null
for ($i = 0; $i -lt 60; $i++) {
    $window = Get-Process -Name MediaRenamer -ErrorAction SilentlyContinue |
        Where-Object { $_.Path -eq $exe -and $_.MainWindowHandle -ne 0 } |
        Select-Object -First 1
    if ($window) { break }
    Start-Sleep -Milliseconds 250
}
if (-not $window) { throw 'A build não abriu a janela dentro do prazo.' }
if ($window.MainWindowTitle -ne 'Renomeador de Mídia') { throw 'Título inesperado.' }
$null = $window.Handle
if (-not $window.CloseMainWindow()) { throw 'Não foi possível fechar a janela normalmente.' }
if (-not $window.WaitForExit(15000)) { throw 'A janela não encerrou dentro do prazo.' }
if (-not $started.WaitForExit(15000)) { throw 'O processo inicial não encerrou dentro do prazo.' }
Write-Output ('Códigos de saída: janela={0}; inicial={1}' -f $window.ExitCode, $started.ExitCode)
if ($null -eq $window.ExitCode -or $null -eq $started.ExitCode -or $window.ExitCode -ne 0 -or $started.ExitCode -ne 0) { throw 'A build encerrou com erro ou código de saída indisponível.' }
Write-Output 'Executável: janela abriu e encerrou normalmente.'
'''
    subprocess.run(['powershell.exe', '-NoProfile', '-Command', code],
                   env=env, check=True, timeout=55)


def main():
    if os.name != 'nt':
        raise SystemExit('Execute com o Python do Windows, inclusive quando chamado do WSL.')
    # Nenhuma atualização/instalação automática de dependências.
    packages = {name: version(name) for name in PACKAGES}
    for name, installed in packages.items():
        requirements = (SOURCE / 'requirements.txt').read_text() + (SOURCE / 'requirements-build.txt').read_text()
        if f'{name.lower()}=={installed}' not in requirements.lower():
            raise SystemExit(f'Versão instalada diverge do ambiente validado: {name}=={installed}')
    for folder in ('tests', 'scripts'):
        subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(ROOT / folder),
                        '-p', 'test_*.py', '-v'], check=True)
    identifier = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    backup = ROOT / 'backups' / ('MediaRenamer_' + identifier)
    backup.mkdir(parents=True, exist_ok=False)
    previous = {}
    for index, path in enumerate(ACTIVE):
        if path.exists():
            saved = backup / f'{index}_MediaRenamer.exe'
            shutil.copy2(path, saved)
            if sha(saved) != sha(path):
                raise RuntimeError(f'Falha ao conferir backup: {path}')
            previous[path.relative_to(ROOT).as_posix()] = sha(saved)
    (backup/'manifest.json').write_text(json.dumps(previous, indent=2)+'\n', encoding='utf-8')
    inputs = sorted([*SOURCE.glob('*.py'), *SOURCE.glob('*.spec'), *SOURCE.glob('requirements*.txt')])
    hashes = {p.name: sha(p) for p in inputs}
    with tempfile.TemporaryDirectory(prefix='mrenamer-build-') as temporary:
        stage = Path(temporary)
        for path in inputs:
            shutil.copy2(path, stage / path.name)
        subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
                        'media_renamer.spec'], cwd=stage, check=True)
        executable = stage/'dist'/'MediaRenamer.exe'
        if executable.read_bytes()[:2] != b'MZ':
            raise RuntimeError('Saída não é um executável Windows PE.')
        profile = stage/'smoke-profile'
        profile.mkdir()
        smoke(executable, profile)
        if any(sha(SOURCE/name) != expected for name, expected in hashes.items()):
            raise RuntimeError('Fontes alteradas durante a build. Distribuição cancelada.')
        expected = sha(executable)
        # Prepara todas as cópias antes de substituir as versões ativas.
        pending = []
        updated = []
        try:
            for target in ACTIVE:
                target.parent.mkdir(parents=True, exist_ok=True)
                candidate = target.with_name(f'.MediaRenamer-{identifier}.pending')
                shutil.copy2(executable, candidate)
                if sha(candidate) != expected:
                    raise RuntimeError(f'Cópia inválida: {candidate}')
                pending.append((target, candidate))
            for target, candidate in pending:
                candidate.replace(target)
                updated.append(target)
        except OSError:
            for target in updated:
                index = ACTIVE.index(target)
                original = backup / f'{index}_MediaRenamer.exe'
                if original.exists():
                    shutil.copy2(original, target)
            raise
        finally:
            for _, candidate in pending:
                candidate.unlink(missing_ok=True)
        manifest = dict(built_at=identifier, python=platform.python_version(),
                        platform=platform.platform(), packages=packages, inputs=hashes,
                        executable_sha256=expected,
                        active_paths=[p.relative_to(ROOT).as_posix() for p in ACTIVE],
                        validation='unittest Windows + Tk integration + executable open/close')
        (ROOT/'renamer final'/'build-manifest.json').write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
        for path in ACTIVE:
            if sha(path) != expected:
                raise RuntimeError(f'Distribuição divergente: {path}')
        print(f'Build entregue: {expected}\nBackup: {backup.name}')


if __name__ == '__main__':
    main()
