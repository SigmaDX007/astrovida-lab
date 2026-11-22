"""Conectores de leitura a arquivos de pesquisa públicos."""
from __future__ import annotations
import hashlib
import io
from pathlib import Path
import numpy as np
import pandas as pd
import requests

TAP_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
PS_COLUMNS = (
    "pl_name", "hostname", "ra", "dec", "pl_rade", "pl_eqt", "pl_orbper",
    "pl_orbsmax", "st_teff", "sy_dist", "disc_year", "discoverymethod",
)

def exoplanet_query(limit: int = 500, search_name: str = "") -> tuple[pd.DataFrame, str]:
    """ADQL com parâmetros controlados; nome filtrado localmente."""
    if not 1 <= int(limit) <= 2000:
        raise ValueError("Limite deve estar entre 1 e 2000")
    query = (f"select top {int(limit)} {','.join(PS_COLUMNS)} "
             "from pscomppars where pl_rade is not null and pl_eqt is not null "
             "order by pl_rade asc")
    request = requests.Request("GET", TAP_URL, params={"query": query, "format": "csv"}).prepare()
    response = requests.get(TAP_URL, params={"query": query, "format": "csv"}, timeout=45)
    response.raise_for_status()
    data = pd.read_csv(io.StringIO(response.text))
    if not set(PS_COLUMNS).issubset(data.columns):
        raise ValueError("Esquema inesperado da NASA TAP")
    if search_name.strip():
        data = data[data["pl_name"].str.contains(search_name.strip(), regex=False, case=False, na=False)]
    return data.reset_index(drop=True), request.url

def load_spectrum_fits(path: str | Path):
    """Extrai WAVELENGTH/FLUX de FITS 1D; não é profundidade de trânsito."""
    from astropy.io import fits
    with fits.open(path, memmap=False) as hdus:
        for hdu in hdus:
            values = getattr(hdu, "data", None)
            names = (getattr(values, "names", None) or ()) if values is not None else ()
            mapping = {str(name).upper(): name for name in names}
            if {"WAVELENGTH", "FLUX"}.issubset(mapping):
                wav = np.asarray(values[mapping["WAVELENGTH"]], dtype=float).ravel().copy()
                flux = np.asarray(values[mapping["FLUX"]], dtype=float).ravel().copy()
                if wav.size >= 5 and wav.size == flux.size:
                    return pd.DataFrame({"wavelength": wav, "value": flux}), str(hdu.name)
    raise ValueError("Não há tabela WAVELENGTH + FLUX compatível no FITS")

def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fd:
        for part in iter(lambda: fd.read(1024 * 1024), b""):
            digest.update(part)
    return digest.hexdigest()

def mast_jwst_observations(ra: float, dec: float, radius_arcmin: float = 1.5):
    """Busca regional JWST; exige astroquery e rede."""
    from astroquery.mast import Observations
    from astropy.coordinates import SkyCoord
    import astropy.units as u
    if not (-90 <= dec <= 90 and 0 <= ra < 360 and 0 < radius_arcmin <= 5):
        raise ValueError("Coordenadas ou raio inválidos")
    table = Observations.query_region(SkyCoord(ra, dec, unit="deg"),
                                      radius=radius_arcmin * u.arcmin)
    if "obs_collection" not in table.colnames:
        raise RuntimeError("Resposta MAST sem coluna obs_collection")
    return table[table["obs_collection"] == "JWST"]

def mast_x1d_products(observation_table):
    from astroquery.mast import Observations
    if len(observation_table) == 0:
        return []
    products = Observations.get_product_list(observation_table)
    if "productFilename" not in products.colnames:
        return products[:0]
    return products[[str(name).lower().endswith("_x1d.fits")
                     for name in products["productFilename"]]]

def mast_download_one(product_row, directory: str | Path, size_limit_mb: int = 80):
    from astroquery.mast import Observations
    size = float(product_row["size"][0]) if "size" in product_row.colnames else 0
    if size and size > size_limit_mb * 1024 * 1024:
        raise ValueError("Arquivo excede limite de download")
    dest = Path(directory)
    dest.mkdir(parents=True, exist_ok=True)
    manifest = Observations.download_products(product_row, download_dir=str(dest))
    valid = manifest[manifest["Status"] == "COMPLETE"]
    if not len(valid):
        raise RuntimeError("MAST não confirmou download")
    return Path(str(valid["Local Path"][0]))
