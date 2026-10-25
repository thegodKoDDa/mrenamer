# Compatibilidade com comandos antigos; especificação única em media_renamer.spec.
from pathlib import Path
spec = Path(SPECPATH) / 'media_renamer.spec'
exec(compile(spec.read_text(encoding='utf-8'), str(spec), 'exec'))
