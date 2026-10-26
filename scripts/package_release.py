"""Prepara assets públicos de uma build validada, sem incluir dados locais."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('renamer/Renomeador_de_Midia_Projeto')
ACTIVE = ['renamer final/MediaRenamer.exe', (SOURCE/'dist/MediaRenamer.exe').as_posix()]
ASSETS = ('MediaRenamer.exe', 'MediaRenamer-Windows-x64.zip', 'build-manifest.json')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_assets(folder):
    folder = Path(folder)
    lines = (folder/'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines()
    expected = {}
    for line in lines:
        if not re.fullmatch(r'[0-9a-f]{64}  [A-Za-z0-9_.-]+', line):
            raise ValueError('Lista de hashes inválida.')
        digest, name = line.split('  ')
        if name in expected:
            raise ValueError('Asset repetido na lista de hashes.')
        expected[name] = digest
    if set(expected) != set(ASSETS):
        raise ValueError('Inventário de assets divergente.')
    for name, digest in expected.items():
        if sha(folder/name) != digest:
            raise ValueError(f'Hash divergente: {name}')
    manifest = json.loads((folder/'build-manifest.json').read_text(encoding='utf-8'))
    if manifest['executable_sha256'] != expected['MediaRenamer.exe']:
        raise ValueError('Executável diverge do manifesto.')
    with zipfile.ZipFile(folder/ASSETS[1]) as archive:
        if sorted(archive.namelist()) != ['GUIA_DO_USUARIO.txt', 'MediaRenamer.exe', 'build-manifest.json']:
            raise ValueError('Conteúdo inesperado no ZIP portátil.')
        for name in ('MediaRenamer.exe', 'build-manifest.json'):
            if archive.read(name) != (folder/name).read_bytes():
                raise ValueError(f'Conteúdo do ZIP divergente: {name}')
    return expected


def package(root, output, commit):
    root, output = Path(root), Path(output)
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('Informe o SHA completo do commit das fontes.')
    manifest = json.loads((root/'renamer final/build-manifest.json').read_text(encoding='utf-8'))
    if manifest['active_paths'] != ACTIVE:
        raise ValueError('Caminhos ativos inesperados no manifesto.')
    source = root/SOURCE
    inputs = {p.name for pattern in ('*.py', '*.spec', 'requirements*.txt') for p in source.glob(pattern)}
    if set(manifest['inputs']) != inputs:
        raise ValueError('Inventário de fontes divergente da build.')
    for name, digest in manifest['inputs'].items():
        if Path(name).name != name or sha(source/name) != digest:
            raise ValueError(f'Fonte alterada após a build: {name}')
    for name in ACTIVE:
        if sha(root/name) != manifest['executable_sha256']:
            raise ValueError(f'Executável ativo divergente: {name}')
    executable = root/ACTIVE[0]
    data = executable.read_bytes()
    offset = int.from_bytes(data[60:64], 'little')
    if (data[:2] != b'MZ' or offset < 64 or data[offset:offset+6] != b'PE\x00\x00\x64\x86'):
        raise ValueError('A distribuição exige um executável PE Windows x64.')
    guide = (root/'renamer final/GUIA_DO_USUARIO.txt').read_bytes()
    manifest = {**manifest, 'source_commit': commit, 'distribution': 'Windows x64'}
    output.mkdir(parents=True, exist_ok=False)
    shutil.copy2(executable, output/'MediaRenamer.exe')
    (output/'build-manifest.json').write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    with zipfile.ZipFile(output/ASSETS[1], 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.write(output/'MediaRenamer.exe', 'MediaRenamer.exe')
        archive.write(output/'build-manifest.json', 'build-manifest.json')
        archive.writestr('GUIA_DO_USUARIO.txt', guide)
    (output/'SHA256SUMS.txt').write_text(
        ''.join(f'{sha(output/name)}  {name}\n' for name in ASSETS), encoding='utf-8')
    verify_assets(output)
    (output/'release-notes.md').write_text(f'''## Usar no Windows (64 bits)

- **MediaRenamer.exe**: baixe e abra. Não precisa instalar Python.
- **MediaRenamer-Windows-x64.zip**: extraia e abra MediaRenamer.exe; inclui guia rápido e manifesto.
- **Source code**: código desta versão para executar com Python ou compilar por conta própria.

O executável preserva as extensões e oferece prévia, sequências, substituição, desfazer na sessão e recuperação assistida de lotes interrompidos.

[Manual](https://github.com/thegodKoDDa/mrenamer/blob/{commit}/docs/user-guide.md) · [Limites conhecidos](https://github.com/thegodKoDDa/mrenamer/blob/{commit}/docs/KNOWN_ISSUES.md)

## Verificação

Build submetida aos testes Windows/Tk e ao teste de abertura/fechamento do executável. SHA-256 de MediaRenamer.exe: `{manifest['executable_sha256']}`.

SHA256SUMS.txt permite conferir os downloads; build-manifest.json registra fontes, ambiente e commit `{commit}`. Hashes verificam integridade, sem substituir assinatura digital. O executável ainda não possui assinatura digital.

Para atualizar uma cópia anterior, feche o aplicativo e baixe a versão mais recente. Não há atualização automática dentro do aplicativo. As preferências permanecem no perfil do usuário.
''', encoding='utf-8')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--commit')
    parser.add_argument('--verify-dir', type=Path)
    args = parser.parse_args()
    if args.verify_dir:
        verify_assets(args.verify_dir)
        print('Assets baixados e hashes conferidos.')
    else:
        if not args.output or not args.commit:
            parser.error('Use --output e --commit, ou --verify-dir.')
        print(f'Assets preparados e conferidos: {package(ROOT, args.output, args.commit)}')


if __name__ == '__main__':
    main()
