"""Indicadores exploratórios, sem alegações de detecção de vida."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Iterable
import numpy as np
from scipy.stats import permutation_test

@dataclass(frozen=True)
class ContrastResult:
    status: str
    n_feature: int
    n_control: int
    feature_median: float
    control_median: float
    effect: float
    p_value: float
    ci_low: float
    ci_high: float
    direction: str
    caveat: str = (
        "Teste exploratório: pixels correlacionados, sistema instrumental, seleção "
        "de janelas e múltiplas comparações podem invalidar a significância. "
        "Uma feição espectral não identifica molécula nem comprova vida."
    )

def spectral_contrast(
    wavelength: Iterable[float],
    value: Iterable[float],
    feature: tuple[float, float],
    controls: tuple[tuple[float, float], tuple[float, float]],
    direction: str = "less",
    *,
    seed: int = 42,
    resamples: int = 999,
) -> ContrastResult:
    """H0: distribuição dos valores na janela alvo equivale ao controle.

    Unidade amostral é pixel; aproximação que NÃO modela ruído correlacionado.
    """
    if direction not in ("less", "greater", "two-sided"):
        raise ValueError("direction inválida")
    if any(not (np.isfinite(a) and np.isfinite(b) and a < b)
           for a, b in (feature, *controls)):
        raise ValueError("Janelas devem ser finitas e ter limites crescentes")
    x = np.asarray(list(wavelength), dtype=float)
    y = np.asarray(list(value), dtype=float)
    if x.ndim != 1 or y.ndim != 1 or len(x) != len(y):
        raise ValueError("Comprimentos de onda e valores incompatíveis")
    valid = np.isfinite(x) & np.isfinite(y)
    target_mask = (x >= feature[0]) & (x <= feature[1]) & valid
    ctrl_mask = (((x >= controls[0][0]) & (x <= controls[0][1])) |
                 ((x >= controls[1][0]) & (x <= controls[1][1]))) & valid
    if np.any(target_mask & ctrl_mask):
        raise ValueError("Janelas de alvo e controle se sobrepõem")
    target, ctrl = y[target_mask], y[ctrl_mask]
    if len(target) < 5 or len(ctrl) < 5:
        raise ValueError("Use ao menos 5 pontos finitos em cada região")

    def statistic(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.median(a) - np.median(b))

    p = permutation_test(
        (target, ctrl), statistic, permutation_type="independent",
        alternative=direction, n_resamples=resamples, random_state=seed,
    ).pvalue
    rng = np.random.default_rng(seed)
    boot = np.array([
        statistic(rng.choice(target, len(target), replace=True),
                  rng.choice(ctrl, len(ctrl), replace=True))
        for _ in range(resamples)
    ])
    low, high = np.quantile(boot, [0.025, 0.975])
    return ContrastResult(
        status="CONTRASTE_EXPLORATORIO", n_feature=len(target), n_control=len(ctrl),
        feature_median=float(np.median(target)), control_median=float(np.median(ctrl)),
        effect=statistic(target, ctrl), p_value=float(p),
        ci_low=float(low), ci_high=float(high), direction=direction,
    )

def candidate_score(radius: float | None, equilibrium_k: float | None) -> float | None:
    """Pontuação de triagem [0,100], NÃO probabilidade de vida."""
    if radius is None or equilibrium_k is None:
        return None
    try:
        r, t = float(radius), float(equilibrium_k)
    except (ValueError, TypeError):
        return None
    if not (np.isfinite(r) and np.isfinite(t) and r > 0 and t > 0):
        return None
    radius_factor = max(0.0, 1.0 - abs(r - 1.0) / 2.5)
    temp_factor = max(0.0, 1.0 - abs(t - 255.0) / 230.0)
    return round(100.0 * radius_factor * temp_factor, 2)

def demo_spectrum(with_feature: bool = True, seed: int = 21):
    """SIMULAÇÃO, jamais confundir com JWST."""
    rng = np.random.default_rng(seed)
    x = np.linspace(1.0, 5.0, 240)
    y = 1.0 + rng.normal(0, 0.015, size=x.size)
    if with_feature:
        y -= 0.12 * np.exp(-0.5 * ((x - 3.3) / 0.075) ** 2)
    return x, y

def to_dict(result: ContrastResult):
    return asdict(result)
