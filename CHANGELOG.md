# Changelog

## 2026-10-26

### Adicionado

- Download público de EXE Windows x64 e ZIP portátil em Releases, com links para a última versão estável.
- Publicação automática após mudanças do aplicativo em main, condicionada a testes, build, smoke e hashes dos assets remotos.

- Recuperação assistida em Configurações, com inspeção do mapa, prévia e confirmação antes de restaurar os nomes.
- Mapas versão 2 com identidade, tamanho e data de modificação dos arquivos; suporte a lotes em subpastas pela pasta ancestral comum.
- Benchmark reproduzível com 1.000 e 10.000 arquivos fictícios.
- Testes de interrupção abrupta, recuperação, conflitos, subpastas, drop com Unicode e escalas Tk de 100%, 150% e 200%.

### Ajustado

- Inicialização usa a escala do Tk e limita o tamanho da janela à tela; a altura das linhas acompanha a fonte.
- Documentação, README e navegação do repositório reorganizados; adicionados guia de contribuição e modelos de issues.
- Apresentação com captura real da interface usando dados fictícios e selo de verificações; integração contínua no Linux e no Windows.

A distribuição Windows foi reconstruída e validada nas duas cópias locais, com backups individuais. Mapas versão 1 continuam exigindo recuperação manual.

## 2026-10-25

### Corrigido

- Validação global de nomes, conflitos e extensões antes de renomear.
- Proteção contra sobrescrita e restauração após falhas, com mapa persistente para recuperação.
- Desfazer com suporte a trocas e ciclos de nomes.
- Prévia separada para Padrão e Substituição; substituição preserva a extensão.
- Entradas numéricas inválidas bloqueadas com mensagem na interface.
- Monitoramento de pastas em thread, com descarte de resultados desatualizados.

### Adicionado

- Motor independente da interface e suíte de regressão e integração Windows.
- Build com dependências fixadas, backups, teste de abertura/fechamento e manifesto de proveniência.
- Documentação de uso, desenvolvimento e recuperação; checkpoints locais verificados.
- Publicação do código-fonte no GitHub, com originais históricos preservados.
