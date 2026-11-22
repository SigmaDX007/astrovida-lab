# AstroVida Lab

Laboratório independente para investigar hipóteses falsificáveis sobre vida extraterrestre, com fontes astronômicas reais, análise exploratória e caderno auditável.

> Anomalias e valores-p não comprovam vida extraterrestre. Nenhuma análise sintética é uma observação do JWST.

## Executar (Windows / Git Bash)

Requisitos: Git, Python 3.11+ e internet para instalar pacotes na primeira execução.

```bash
git clone https://github.com/SigmaDX007/astrovida-lab.git && cd astrovida-lab && bash run.sh
```

O script inicializa a venv, instala dependências somente quando necessário, executa testes offline e abre o dashboard Streamlit em http://127.0.0.1:8501.

Somente testes: `bash run.sh --check`.

## Recursos

- NASA Exoplanet Archive TAP: consulta de catálogo planetário, ranking heurístico (não probabilidade de vida).
- MAST / JWST: busca de observações públicas por RA/Dec e arquivos espectrais FITS X1D.
- Espectroscopia: simulações identificadas, upload CSV/FITS, contraste de medianas, permutação e bootstrap.
- Caderno: H0/H1, previsões, falsificação, confundidores, registros de execução com fonte, SHA256, parâmetros, UTC e commit.
- Fontes para integração futura: TESS, Kepler, Gaia, Breakthrough Listen, ALMA e NASA PDS.

## Estrutura

`app.py` dashboard | `alienlab/` ciência e dados | `tests/` testes offline | `docs/` hipóteses, fontes, decisões, status e backlog | `run.sh` execução.

Os arquivos pessoais e espectros baixados ficam em `local_data/` (ignorado pelo Git). Como este repositório foi criado **público**, não inclua dados privados, chaves ou arquivos grandes no controle de versão.

### Limites científicos

- FITS X1D não é necessariamente espectro de transmissão de exoplaneta. A inferência molecular requer redução e modelagem instrumentais.
- p-valor de um contraste exploratório não prova molécula, biossinal, tecnologia ou habitabilidade.
- Os testes locais são sintéticos/mock: o comportamento dos serviços NASA e MAST requer verificação online separada.
