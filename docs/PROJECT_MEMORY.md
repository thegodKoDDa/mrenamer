# Memória do projeto

- Nome da pasta: `mrenamer`; produto: Renomeador de Mídia/MediaRenamer. Local: `/home/gabriel/dev/mrenamer`.
- Pedido de 25/10/2026: revisão geral e organização seguindo os padrões do EletroProjeto e projetos recentes. Referências locais consultadas: EletroProjeto e Minecoord.
- Adotados: instruções na raiz, estado/memória/histórico, separação documental, exclusões de Git e checkpoints com recuperação isolada.
- Stack própria preservada: Python 3.10+, Tkinter/ttk, tkinterdnd2, PyInstaller; distribuição Windows. Não é aplicação web e não usa os cálculos ou bancos do EletroProjeto.
- Fonte atual: arquivo de 1.294 linhas em `renamer/Renomeador_de_Midia_Projeto/media_renamer.py`. Fonte original: 278 linhas em `renamer original/Renomeador_de_Midia.py`.
- Caminhos de fontes e distribuição mantidos nesta etapa para não alterar compatibilidade nem exigir recompilação por uma reorganização física. Código do aplicativo, requirements, specs e executáveis não foram alterados.
- Regra preexistente de recompilação e backup obrigatório de executáveis preservada; aplica-se ao aplicativo. Scripts de continuidade não fazem parte do produto empacotado.
- Não existia `.git` nem remoto na inspeção inicial. Não existe autorização específica de publicação deste projeto; permissões remotas de projetos vizinhos não se transferem.
- Preferências reais ficam em `~/.media_renamer.json`, fora da raiz. Mídias ficam nas pastas escolhidas pelo usuário; não são dados internos do projeto.
- O backup inicial completo é `.checkpoints/before-organization/`; inclui os 90 arquivos iniciais, com manifesto SHA-256. Backups herdados não foram removidos ou deduplicados.
- Organização incluiu inicialização do Git local na branch main e baseline revisado; sem remoto. Executáveis, checkpoints e backups ficam ignorados.
- Pedido posterior de 25/10/2026: publicar no GitHub em repositório público. Destino criado: `thegodKoDDa/mrenamer`, remoto origin HTTPS. Publicação restrita às fontes e documentação revisadas; executáveis, backups e checkpoints permanecem locais.
