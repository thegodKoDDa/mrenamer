# Continuidade e recuperação

## Rotina

Na raiz: `python3 scripts/continuity.py retomar`. Leia CURRENT_STATE e PROJECT_MEMORY; a rotina informa dependências do Python que a executa, Git e ponteiro do último checkpoint. Não instala nada, inicia serviços ou consulta remotos.

Antes de mudanças estruturais e ao encerrar: `python3 scripts/continuity.py encerrar`. Captura fontes, documentos, ferramentas, originais e executáveis de distribuição em `source.zip`, grava manifesto SHA-256, extrai em diretório temporário e compara inventário e hashes. Somente após sucesso atualiza `.checkpoints/latest.json`. `verificar` repete a recuperação isolada. Windows usa `python` nos mesmos comandos.

Não executar durante builds ou gravações concorrentes. A captura é por arquivo, sem snapshot atômico do sistema. Uma rotina por vez. Diretórios e arquivos novos do checkpoint recebem permissões privadas no POSIX; isso não configura ACLs Windows.

## Conteúdo

Excluídos dos pontos rotineiros: `.git`, `.checkpoints`, ambientes virtuais, caches listados no script, node_modules, `build/`, `backups/`, `.env*` privados, pyc e Zone.Identifier. `dist/` e a distribuição principal entram, pois permitem recuperar a versão entregue. ZIPs originais dentro da árvore também entram. Links simbólicos não são seguidos.

O ponto inicial `.checkpoints/before-organization/` contém todos os 90 arquivos anteriores à organização, incluindo backups e gerados. Seu manifesto permite comprovar preservação; não é substituído por pontos novos. Backups históricos permanecem também nos caminhos originais.

Não entram: preferências em `~/.media_renamer.json`, mídias externas e histórico Git. Manter cópias próprias desses dados quando necessário. Checkpoint no mesmo disco não é backup externo. A rotina não faz commit/push nem arquiva futuras credenciais com nomes arbitrários automaticamente; revisar arquivos antes de adicioná-los à raiz.

## Restaurar sem sobrescrever

Execute `verificar`, consulte `latest.json` e extraia o ZIP indicado para uma pasta nova. Preserve a árvore atual. Dependências podem ser reinstaladas nessa cópia; execute/teste o produto no Windows. Para verificar o ponto inicial: `python3 -c "from scripts.continuity import verify, CHECKPOINTS; print(verify(CHECKPOINTS / 'before-organization'))"`.

Os checkpoints são locais e ignorados pelo Git. Nenhum é apagado automaticamente.
