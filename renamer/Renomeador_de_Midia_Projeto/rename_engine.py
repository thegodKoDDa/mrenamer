"""Validação e renomeação de arquivos, sem dependências de interface gráfica."""
import json
import os
from pathlib import Path
import re
import uuid


RESERVED = {'CON', 'PRN', 'AUX', 'NUL', 'CONIN$', 'CONOUT$'} | {
    f'{prefix}{number}' for prefix in ('COM', 'LPT')
    for number in '123456789¹²³'
}


def validate_name(name):
    if (not name or name in {'.', '..'} or name.endswith((' ', '.'))
            or re.search(r'[<>:"/\\|?*\x00-\x1f]', name)
            or name.split('.')[0].rstrip(' ').upper() in RESERVED):
        raise ValueError(f'Nome inválido no Windows: {name!r}')
    if len(name.encode('utf-16-le')) // 2 > 255:
        raise ValueError('O nome ultrapassa 255 caracteres UTF-16.')
    return name


def replace_stem(path, search, replacement):
    """Preserva a extensão mesmo quando o texto procurado ocorre nela."""
    path = Path(path)
    stem = path.stem.replace(search, replacement) if search else path.stem
    if not stem.strip() or stem.endswith((' ', '.')):
        raise ValueError('O nome antes da extensão não pode ficar vazio ou terminar em espaço/ponto.')
    return validate_name(stem + path.suffix)


def path_key(path):
    return str(Path(path).absolute()).casefold()


def validate_operations(operations):
    operations = [(Path(old).absolute(), Path(new).absolute()) for old, new in operations]
    sources = {path_key(old) for old, _ in operations}
    if len(sources) != len(operations):
        raise ValueError('O lote contém arquivos de origem repetidos.')
    targets = set()
    # Inventário por pasta para detectar colisões Windows também em testes POSIX.
    entries = {}
    for old, new in operations:
        validate_name(new.name)
        if old.parent != new.parent:
            raise ValueError('A renomeação deve manter cada arquivo na própria pasta.')
        if old.suffix != new.suffix:
            raise ValueError('A extensão original deve ser preservada.')
        if old.is_symlink() or not old.is_file():
            raise ValueError(f'Origem indisponível ou link simbólico: {old}')
        key = path_key(new)
        if key in targets:
            raise ValueError(f'O lote gera nomes duplicados: {new.name}')
        targets.add(key)
        if old.parent not in entries:
            entries[old.parent] = {path_key(p): p for p in old.parent.iterdir()}
        if key in entries[old.parent] and key not in sources:
            raise FileExistsError(f'O destino já existe e não será sobrescrito: {new}')
    return [(old, new) for old, new in operations if str(old) != str(new)]


def move_no_replace(source, target):
    """Move sem substituir um destino criado por outro processo."""
    if os.name == 'nt':
        os.rename(source, target)
    else:
        # rename() POSIX sobrescreve destinos: link exclusivo evita essa perda.
        os.link(source, target, follow_symlinks=False)
        try:
            source.unlink()
        except OSError:
            target.unlink()
            raise


class RenameTransactionError(Exception):
    def __init__(self, cause, completed, rolled_back, journal, locations):
        self.completed = completed
        self.rolled_back = rolled_back
        self.journal = journal
        message = f'{cause}\n\n{completed} destino(s) concluído(s) antes da falha.'
        if rolled_back:
            message += '\nTodos os arquivos foram restaurados aos nomes anteriores.'
        else:
            message += (f'\nA restauração ficou incompleta. Não repita o lote.\n'
                        f'Mapa para recuperação: {journal}\nArquivos preservados em:\n'
                        + '\n'.join(str(p) for p in locations))
        super().__init__(message)


def rename_batch(operations, progress=None):
    operations = validate_operations(operations)
    if progress is not None:
        progress[0] = 0
    if not operations:
        return []
    identifier = uuid.uuid4().hex
    records = [dict(original=str(old), temporary=str(old.with_name(
        f'.__renamer_tmp_{identifier}_{i}{old.suffix}')), target=str(new),
        identity=[old.stat().st_dev, old.stat().st_ino])
        for i, (old, new) in enumerate(operations)]
    journal = operations[0][0].parent / f'.__renamer_recovery_{identifier}.json'
    # Mapa persistido ANTES do primeiro movimento. Ajuda em queda de energia ou
    # bloqueio durante rollback, sem alegar transação atômica do sistema inteiro.
    with journal.open('x', encoding='utf-8') as stream:
        json.dump({'version': 1, 'operations': records}, stream, ensure_ascii=False, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    current = [Path(r['original']) for r in records]
    completed = 0
    try:
        for i, record in enumerate(records):
            temporary = Path(record['temporary'])
            move_no_replace(current[i], temporary)
            current[i] = temporary
        for i, record in enumerate(records):
            target = Path(record['target'])
            move_no_replace(current[i], target)
            current[i] = target
            completed += 1
            if progress is not None:
                progress[0] = completed
    except OSError as cause:
        # Primeiro libera todos os nomes finais (inclusive ciclos), depois
        # restaura as origens. Nunca substitui arquivos externos ao lote.
        for i in range(completed):
            temporary = Path(records[i]['temporary'])
            try:
                move_no_replace(current[i], temporary)
                current[i] = temporary
            except OSError:
                pass
        for i, record in enumerate(records):
            original = Path(record['original'])
            if current[i] == original:
                continue
            try:
                move_no_replace(current[i], original)
                current[i] = original
            except OSError:
                pass
        restored = all(p == Path(r['original']) for p, r in zip(current, records))
        if restored:
            try:
                journal.unlink()
            except OSError:
                pass
        raise RenameTransactionError(cause, completed, restored, journal, current) from cause
    try:
        journal.unlink()
    except OSError:
        # Arquivos já chegaram aos destinos. Um mapa residual não desfaz sucesso.
        pass
    return operations
