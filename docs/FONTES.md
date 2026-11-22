# Fontes científicas públicas

| Fonte oficial | Dados reais | Implementação |
|---|---|---|
| [NASA Exoplanet Archive TAP](https://exoplanetarchive.ipac.caltech.edu/docs/TAP/usingTAP.html) | Planetas, raio, temperatura de equilíbrio, distância, RA/Dec | Integrada, CSV/pscomppars, chamada HTTP |
| [MAST/STScI JWST](https://outerspace.stsci.edu/spaces/MASTDOCS/pages/153686810/MAST+Primer+for+JWST) | Observações e espectros FITS X1D | Integrada, busca astroquery por coordenada, download limitado |
| [MAST TESS/Kepler](https://mast.stsci.edu/) | Curvas de luz e trânsitos | Link, não automatizada |
| [ESA Gaia](https://gea.esac.esa.int/archive/) | Astrometria e propriedades estelares | Link, não automatizada |
| [Breakthrough Listen](https://seti.berkeley.edu/opendata) | Rádio e tecnossinais candidatos | Link, não automatizada; GB de dados e interferência |
| [NASA PDS](https://pds.nasa.gov/) | Dados de sondas e química planetária | Link, não automatizada |
| [ALMA Science Archive](https://almascience.nrao.edu/aq/) | Química interestelar | Link, não automatizada |

Proveniência: consulta completa NASA/CSV; URI MAST e SHA-256 do FITS; upload hash; parâmetros, UTC, notas e SHA Git na execução. Fonte real pode estar indisponível. A execução ao vivo NASA/MAST não foi confirmada no ambiente de construção.
