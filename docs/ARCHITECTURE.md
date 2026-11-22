# Arquitetura

- app.py: cinco abas Streamlit (NASA, JWST, Espectroscopia, Hipóteses, Fontes).
- alienlab/sources.py: NASA TAP com query controlada e timeout; astroquery.mast por RA/Dec; FITS X1D via Astropy; SHA256 de artefatos.
- alienlab/core.py: simulação e índice arbitrário de triagem; contraste de medianas com permutação e bootstrap com sementes fixas.
- alienlab/storage.py: SQLite local com hypotheses e runs. Cada execução guarda origem, SHA256, parâmetros JSON, resultados, UTC e commit Git.
- run.sh: venv, hash das dependências, compilação, testes offline e Streamlit.
- tests/: casos positivos/negativos, mocks HTTP, integridade SQLite; não substituem integração real.

Fluxo: pré-registro H0/H1 -> fonte pública/CSV/FITS/simulado -> janelas e controles -> teste exploratório -> auditoria -> replicação independente.

Segurança: SQL parametrizado, tabelas em allowlist, dados locais não versionados, limite de download 80MB, serviços pagos não utilizados.

Lacunas: espectros X1D não são automaticamente espectros de transmissão; inexistem redução físico-instrumental, inferência molecular, FDR, ajuste bayesiano, RFI, Gaia/TESS integrados e sincronização automática.
