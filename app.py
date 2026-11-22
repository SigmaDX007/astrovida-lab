"""AstroVida: interface local Streamlit de pesquisa científica exploratória."""
from __future__ import annotations
import hashlib
from pathlib import Path
import pandas as pd
import streamlit as st

from alienlab.core import candidate_score, demo_spectrum, spectral_contrast, to_dict
from alienlab.sources import (exoplanet_query, load_spectrum_fits, mast_download_one,
                              mast_jwst_observations, mast_x1d_products, sha256_file)
from alienlab.storage import DEFAULT_DB, list_rows, register_hypothesis, report_markdown, save_run

ROOT = Path(__file__).resolve().parent
LOCAL = ROOT / "local_data"
LOCAL.mkdir(exist_ok=True)

st.set_page_config(page_title="AstroVida | Laboratório", page_icon="🔭", layout="wide")
st.title("AstroVida | Laboratório de hipóteses")
st.caption("Exploração com fontes auditáveis. Nenhum ranking, p-valor ou contraste demonstra vida fora da Terra.")

with st.sidebar:
    st.header("Protocolo científico")
    st.markdown("""1. Registre uma hipótese falsificável.
2. Obtenha dados públicos ou importe um arquivo.
3. Defina feição e controles antes de examinar os resultados.
4. Execute e registre origem, SHA-256, parâmetros e limitações.
5. Replique com outros instrumentos e modelos físicos.""")
    st.info("Execuções ficam em local_data/, ignorado pelo Git. Não há API paga.")

nasa_tab, jwst_tab, spectrum_tab, log_tab, sources_tab = st.tabs([
    "NASA | Exoplanetas", "JWST | MAST", "Espectroscopia", "Hipóteses e resultados", "Outras fontes"
])

with nasa_tab:
    st.subheader("Triagem de exoplanetas reais")
    st.caption("NASA Exoplanet Archive / TAP: pscomppars. A amostra é limitada pela consulta, não é censo nem probabilidade de vida.")
    col1, col2 = st.columns([1, 2])
    with col1:
        limit = st.number_input("Máximo de linhas", 50, 2000, 500, 50)
        name_filter = st.text_input("Filtrar nome após download (opcional)")
        if st.button("Consultar NASA", type="primary"):
            try:
                with st.spinner("Consultando catálogo público..."):
                    df, url = exoplanet_query(int(limit))
                st.session_state["nasa_raw"] = df
                st.session_state["nasa_url"] = url
            except Exception as exc:
                st.error(f"Consulta NASA falhou: {exc}")
    if "nasa_raw" in st.session_state:
        data = st.session_state["nasa_raw"].copy()
        if name_filter:
            data = data[data.pl_name.str.contains(name_filter, regex=False, case=False, na=False)]
        data["triagem_heuristica_0a100"] = [
            candidate_score(r, t) for r, t in zip(data.pl_rade, data.pl_eqt)
        ]
        data = data.sort_values("triagem_heuristica_0a100", ascending=False)
        with col2:
            st.metric("Planetas na amostra filtrada", len(data))
            st.caption("Índice de prioridade de estudo: raio terrestre e T_eq moderada. Não mede habitabilidade ou existência de vida.")
            st.dataframe(data, use_container_width=True, hide_index=True)
            st.download_button("Exportar amostra NASA", data.to_csv(index=False).encode("utf-8"), "nasa_amostra.csv", "text/csv")
            st.caption("Consulta original: " + st.session_state["nasa_url"])
        if len(data):
            selected = st.selectbox("Usar coordenadas no MAST", data.pl_name.tolist())
            planet = data.loc[data.pl_name == selected].iloc[0]
            if st.button("Preparar busca JWST desta posição"):
                if pd.notna(planet.ra) and pd.notna(planet.dec):
                    st.session_state["target_coords"] = (float(planet.ra), float(planet.dec))
                    st.success("Coordenadas selecionadas. Abra JWST | MAST.")
                else:
                    st.error("Coordenadas indisponíveis")

with jwst_tab:
    st.subheader("Observações reais do James Webb")
    st.caption("MAST/STScI: busca por coordenadas. Nem todo JWST disponibiliza X1D, e nem todo X1D é espectro de transmissão.")
    ra0, dec0 = st.session_state.get("target_coords", (30.0, 10.0))
    a, b, c = st.columns(3)
    ra = a.number_input("Ascensão reta (graus)", min_value=0.0, max_value=359.9999,
                        value=float(ra0), format="%.5f")
    dec = b.number_input("Declinação (graus)", min_value=-90.0, max_value=90.0,
                         value=float(dec0), format="%.5f")
    radius = c.slider("Raio (minutos de arco)", 0.2, 5.0, 1.5, 0.1)
    if st.button("Buscar observações JWST"):
        try:
            with st.spinner("Consultando MAST..."):
                obs = mast_jwst_observations(ra, dec, radius)
            st.session_state["jwst_obs"] = obs
            st.session_state.pop("jwst_products", None)
        except Exception as exc:
            st.error(f"Falha MAST: {exc}")
    if "jwst_obs" in st.session_state:
        obs = st.session_state["jwst_obs"]
        st.write(f"{len(obs)} observações JWST encontradas na região")
        if len(obs):
            cols = [c for c in ("obs_id", "target_name", "instrument_name", "t_exptime", "dataRights") if c in obs.colnames]
            st.dataframe(obs[cols].to_pandas().head(200), hide_index=True)
            selected_index = st.number_input("Índice da observação", 0, len(obs) - 1, 0)
            if st.button("Listar produtos espectrais X1D"):
                try:
                    products = mast_x1d_products(obs[int(selected_index):int(selected_index) + 1])
                    st.session_state["jwst_products"] = products
                except Exception as exc:
                    st.error(f"Falha ao consultar produtos: {exc}")
        if "jwst_products" in st.session_state:
            prods = st.session_state["jwst_products"]
            st.write(f"{len(prods)} produtos X1D (até 100 na seleção)")
            if len(prods):
                pos = st.selectbox("FITS a baixar", list(range(min(len(prods), 100))),
                                   format_func=lambda i: str(prods["productFilename"][i]))
                if st.button("Baixar FITS selecionado (limite 80 MB)"):
                    try:
                        row = prods[int(pos):int(pos) + 1]
                        path = mast_download_one(row, LOCAL / "mast", size_limit_mb=80)
                        frame, hdu = load_spectrum_fits(path)
                        source_id = str(prods["dataURI"][int(pos)]) if "dataURI" in prods.colnames else str(prods["productFilename"][int(pos)])
                        st.session_state.update(
                            spectrum_frame=frame, spectrum_path=str(path),
                            spectrum_origin=f"MAST/JWST:{source_id} [HDU={hdu}]",
                            spectrum_sha=sha256_file(path)
                        )
                        st.success("Espectro carregado. Abra Espectroscopia.")
                    except Exception as exc:
                        st.error(f"Download/leitura falhou: {exc}")

with spectrum_tab:
    st.subheader("Teste exploratório de feição espectral")
    st.warning("Um contraste em FLUX não identifica molécula; efeitos sistemáticos, unidades, incertezas e múltiplas comparações devem ser avaliados.")
    mode = st.radio("Origem", ["Demonstração sintética", "FITS ou CSV local", "Espectro previamente carregado"], horizontal=True)
    frame, source, digest = None, "", ""
    if mode == "Demonstração sintética":
        feature_exists = st.checkbox("Injetar feição artificial", value=True)
        x, y = demo_spectrum(feature_exists)
        frame = pd.DataFrame({"wavelength": x, "value": y})
        source = f"SIMULADO: seed=21, com_feicao={feature_exists}"
        digest = hashlib.sha256(frame.to_csv(index=False).encode()).hexdigest()
    elif mode == "FITS ou CSV local":
        upload = st.file_uploader("Arquivo .fits/.csv (máx. 80 MB)", type=["fits", "csv"])
        if upload is not None:
            if upload.size > 80 * 1024 * 1024:
                st.error("Arquivo maior que 80 MB")
            else:
                content = upload.getvalue()
                digest = hashlib.sha256(content).hexdigest()
                suffix = ".fits" if upload.name.lower().endswith(".fits") else ".csv"
                path = LOCAL / "uploads" / (digest + suffix)
                path.parent.mkdir(exist_ok=True)
                if not path.exists():
                    path.write_bytes(content)
                try:
                    frame = load_spectrum_fits(path)[0] if suffix == ".fits" else pd.read_csv(path)
                    source = f"UPLOAD_LOCAL:{upload.name}"
                except Exception as exc:
                    st.error(f"Erro ao interpretar arquivo: {exc}")
    else:
        frame = st.session_state.get("spectrum_frame")
        source = st.session_state.get("spectrum_origin", "")
        digest = st.session_state.get("spectrum_sha", "")
        if frame is None:
            st.info("Primeiro baixe um X1D do MAST ou use upload.")

    if frame is not None:
        if not {"wavelength", "value"}.issubset(frame.columns):
            st.error("CSV requer colunas numéricas wavelength e value.")
        else:
            st.caption(f"Fonte: {source} | SHA256: {digest}")
            chart = frame[["wavelength", "value"]].copy()
            chart["wavelength"] = pd.to_numeric(chart["wavelength"], errors="coerce")
            chart["value"] = pd.to_numeric(chart["value"], errors="coerce")
            chart = chart.dropna().sort_values("wavelength")
            st.line_chart(chart.set_index("wavelength")["value"])
            if len(chart):
                lo, hi = float(chart.wavelength.min()), float(chart.wavelength.max())
                mid, span = (lo + hi) / 2, hi - lo
                if mode == "Demonstração sintética":
                    defaults = (3.22, 3.38, 3.00, 3.14, 3.46, 3.60)
                else:
                    defaults = (mid - span * .03, mid + span * .03,
                                mid - span * .12, mid - span * .06,
                                mid + span * .06, mid + span * .12)
                st.caption("Janelas padrão são exemplo. Pré-registre as janelas para análise confirmatória.")
                t1, t2, c1, c2, c3, c4 = st.columns(6)
                tlo = t1.number_input("Alvo início", value=round(defaults[0], 5), format="%.5f")
                thi = t2.number_input("Alvo fim", value=round(defaults[1], 5), format="%.5f")
                llo = c1.number_input("Ctrl A início", value=round(defaults[2], 5), format="%.5f")
                lhi = c2.number_input("Ctrl A fim", value=round(defaults[3], 5), format="%.5f")
                rlo = c3.number_input("Ctrl B início", value=round(defaults[4], 5), format="%.5f")
                rhi = c4.number_input("Ctrl B fim", value=round(defaults[5], 5), format="%.5f")
                direction = st.selectbox("Alternativa", ["less", "greater", "two-sided"])
                if st.button("Executar teste de contraste"):
                    try:
                        params = {"feature": [tlo, thi], "controls": [[llo, lhi], [rlo, rhi]],
                                  "direction": direction, "resamples": 999, "seed": 42}
                        result = spectral_contrast(chart.wavelength, chart.value,
                                                   (tlo, thi), ((llo, lhi), (rlo, rhi)),
                                                   direction=direction)
                        st.session_state["latest_test"] = {
                            "source": source, "sha": digest, "parameters": params, "result": to_dict(result)
                        }
                    except Exception as exc:
                        st.error(f"Teste inválido: {exc}")

    if ("latest_test" in st.session_state and frame is not None
            and st.session_state["latest_test"]["sha"] == digest):
        latest = st.session_state["latest_test"]
        st.json(latest)
        st.caption("p-valor não é probabilidade de vida e não corrige seleção a posteriori.")
        hypotheses = list_rows(DEFAULT_DB, "hypotheses")
        if hypotheses:
            hid = st.selectbox("Vincular à hipótese", [h["id"] for h in hypotheses],
                               format_func=lambda ident: next(h["title"] for h in hypotheses if h["id"] == ident))
            notes = st.text_area("Notas/controles/explicações alternativas")
            if st.button("Salvar execução com proveniência"):
                try:
                    runid = save_run(DEFAULT_DB, hypothesis_id=hid, data_origin=latest["source"],
                                     data_sha256=latest["sha"], parameters=latest["parameters"],
                                     results=latest["result"], notes=notes)
                    st.success("Execução registrada: " + runid)
                except Exception as exc:
                    st.error(f"Falha ao salvar: {exc}")
        else:
            st.info("Registre uma hipótese antes de salvar a execução.")

with log_tab:
    st.subheader("Caderno de hipóteses falsificáveis")
    with st.form("new_hypothesis"):
        title = st.text_input("Título")
        claim = st.text_area("Hipótese / interpretação física")
        h0 = st.text_area("Hipótese nula H0", "Não há contraste espectral reprodutível nas janelas predefinidas.")
        prediction = st.text_area("Predição mensurável")
        falsification = st.text_area("Qual resultado refutaria a hipótese?")
        confounders = st.text_area("Explicações alternativas / confundidores",
                                  "Ruído instrumental, estrela hospedeira, calibração e absorção não biológica.")
        if st.form_submit_button("Registrar hipótese", type="primary"):
            try:
                hid = register_hypothesis(DEFAULT_DB, title=title, claim=claim,
                                          null_hypothesis=h0, prediction=prediction,
                                          falsification=falsification, confounders=confounders)
                st.success("Hipótese criada: " + hid)
            except ValueError as exc:
                st.error(str(exc))
    hypotheses = list_rows(DEFAULT_DB, "hypotheses")
    runs = list_rows(DEFAULT_DB, "runs")
    st.metric("Hipóteses", len(hypotheses))
    st.metric("Execuções registradas", len(runs))
    if hypotheses:
        st.dataframe(pd.DataFrame(hypotheses), hide_index=True, use_container_width=True)
    if runs:
        st.dataframe(pd.DataFrame(runs), hide_index=True, use_container_width=True)
    st.download_button("Exportar relatório Markdown", report_markdown(DEFAULT_DB).encode("utf-8"),
                       "astrovida-experimentos.md", "text/markdown")

with sources_tab:
    st.subheader("Mais dados astronômicos públicos")
    st.markdown("""- NASA Exoplanet Archive (TAP): integração na aba NASA.
- MAST/JWST (FITS X1D): integração na aba JWST.
- [MAST/TESS/Kepler](https://mast.stsci.edu/): curvas de luz. Link, não automatizado.
- [ESA Gaia DR3](https://gea.esac.esa.int/archive/): astrometria. Link, não automatizado.
- [Breakthrough Listen](https://seti.berkeley.edu/opendata): tecnossinais de rádio; arquivos podem ter GB. Link, não automatizado.
- [NASA PDS](https://pds.nasa.gov/): dados de sondas. Link, não automatizado.
- [ALMA Science Archive](https://almascience.nrao.edu/aq/): química interestelar. Link, não automatizado.

Condições e controles em docs/. Nenhuma fonte prova vida automaticamente.""")
