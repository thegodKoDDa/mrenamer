# Changelog

## 2026-10-25 — Organização e continuidade

- Revisão do projeto legado e documentação das prioridades técnicas.
- Ponto de entrada documental na raiz, regras de manutenção, estado atual, memória e histórico.
- Recuperação local verificada com manifesto SHA-256, exclusões de gerados/dados privados e três testes automatizados.
- Regras de controle de versão para fontes e documentação; distribuição e backups permanecem locais.
- Aplicativo, identidade visual, caminhos, executáveis e versões anteriores preservados.

## 2026-10-25 — GitHub público

- Repositório público `thegodKoDDa/mrenamer` para código e documentação.
- Executáveis, backups, configurações privadas e checkpoints mantidos locais.

## 2026-10-25 — Correções e build Windows

- Renomeação com validação global, proteção contra sobrescrita e restauração após falhas; mapa persistente para recuperação manual incompleta.
- Desfazer com suporte a trocas/ciclos, extensão preservada e prévias separadas para padrão e substituição.
- Entradas numéricas/nomes Windows validados sem quebrar a interface; progresso de erro correto.
- Monitoramento em thread, descarte de resultados antigos e remoção de buscas repetidas.
- Dependências fixadas, spec consolidado, manuais atualizados e suíte de regressão/integração Windows.
- Nova build Windows testada e distribuída localmente nas duas cópias ativas, com backups individuais e manifesto de proveniência.

## 2026-10-26 — Recuperação assistida e validação de uso

- Recuperação explícita de lotes interrompidos em Configurações: inspeção, prévia, confirmação e revalidação sem sobrescrever destinos.
- Mapas versão 2 com tamanho/data e pasta comum às origens; mapas históricos mantidos para recuperação manual.
- Removida escala fixa na inicialização; janela acompanha escala Tk dentro da tela e linhas acompanham a fonte.
- Regressões para interrupção abrupta de processo, ciclos, conflitos, alterações externas, subpastas, drop Unicode e escalas 100%/150%/200%.
- Benchmark reproduzível de 1.000/10.000 arquivos fictícios e limites físicos/de rede explicitados.
- Build Windows gerada, testada e atualizada nas duas cópias ativas com backups individuais e hashes conferidos; 42 testes Windows aprovados (dois symlinks pulados).
