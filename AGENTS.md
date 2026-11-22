# AstroVida | Instruções para GPT/Codex

**Repositório independente de pesquisa em astrobiologia.** Não utilizar código, dados, lógica ou histórico de projetos comerciais.

1. Antes de alterar, leia README.md e docs/ARCHITECTURE.md, docs/HIPOTESES.md, docs/STATUS.md e docs/BACKLOG.md.
2. Registre H1/H0, predição, falsificação, confundidores, unidades, instrumentos e controles. Nunca apresente p-valores como prova de vida.
3. Identifique evidência como SIMULADO, CATÁLOGO, OBSERVAÇÃO_EXPLORATÓRIA ou REPLICAÇÃO_INDEPENDENTE.
4. Execute testes offline: python -m unittest discover -s tests -v. Mocks não validam integração externa.
5. Armazene SHA-256, UTC, parâmetros e commit; nenhuma API paga nem envio externo de arquivos sem autorização.
6. Repositório público: nunca versionar hipóteses privadas, bancos locais, arquivos FITS ou credenciais.
7. Atualize docs com evidências observadas, não suposições.
