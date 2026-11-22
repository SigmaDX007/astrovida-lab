# Hipóteses iniciais e testes observados

## H-EXEMPLO-01 | Feição artificial em espectro sintético

H1: uma depressão gaussiana artificial centrada em 3.3 unidades deve apresentar contraste negativo.

H0: os fluxos na janela alvo e nos controles têm distribuições equivalentes.

Previsão: mediana menor na janela alvo [3.22, 3.38] do que nos controles [3.00, 3.14] e [3.46, 3.60].

Método: demo_spectrum(True, seed=21); spectral_contrast com direction=less, seed=42, resamples=999; permutação unilateral e bootstrap percentil.

Refutação: efeito não negativo ou falta de suporte sob controles adicionais.

Resultado observado offline em 2026-11-22: diferença de medianas -0.1008712; p nominal 0.001; IC bootstrap 95% [-0.1206373, -0.0746669]; n_alvo=10, n_controle=17.

STATUS: TESTE DE IMPLEMENTAÇÃO SOBRE DADOS SINTÉTICOS. NÃO É DADO JWST NEM EVIDÊNCIA DE VIDA.

## H-EXEMPLO-02 | Controle negativo plano

H0: um espectro artificial constante não contém feição. Mesmo eixo, value=1 em todos os pixels, mesmas janelas.

Resultado observado offline: efeito 0, p=1.0. Controle unitário sem ruído correlacionado. STATUS: SIMULADO.

## H-CIENCIA-01 | Reprodutibilidade de uma feição exoplanetária

H1: uma feição física previamente definida permanece em reduções independentes de observações públicas de um alvo.

H0: a suposta feição é explicada por efeitos instrumentais, estrela hospedeira, ruído, redução ou química abiótica.

Previsão: persistência entre instrumentos/épocas, controle de ruído, modelo físico coerente e observações independentes. Refutação: desaparece após controle/redução, ou explicação abiótica suficiente.

STATUS: NÃO TESTADA COM DADOS REAIS. Exige IDs MAST e espectros de transmissão devidamente reduzidos.

## H-CIENCIA-02 | Tecnossinal de rádio

H0: interferência terrestre, satélite, hardware, efeitos naturais. Predição: sinal repetido on-source e ausente off-source, deriva Doppler e confirmação independente.

STATUS: NÃO TESTADA. Breakthrough Listen tem dados de grande volume e requer blimpy/turboSETI e filtros RFI.

## Protocolo

Registre hipóteses e janelas antes da análise confirmatória. Corrija múltiplos testes, trate ruído correlacionado, documente unidades, controle erros sistemáticos e hipóteses abióticas. Contraste não prova molécula; molécula não prova biologia.
