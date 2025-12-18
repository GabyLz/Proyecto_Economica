import math
import numpy as np
from typing import List, Dict, Any, Tuple
import random

# ---------------------------
# VAN (NPV)
# ---------------------------
def npv(rate: float, cashflows: List[float]) -> float:
    """Valor Actual Neto (rate decimal, cashflows t=0..N)."""
    return float(sum(cf / (1 + rate) ** i for i, cf in enumerate(cashflows)))

# ---------------------------
# TIR (IRR) - Newton + bisección fallback
# ---------------------------
def irr(cashflows: List[float], guess: float = 0.1, tol: float = 1e-8, maxiter: int = 200) -> float:
    cf = np.array(cashflows, dtype=float)

    def f(r):
        periods = np.arange(len(cf))
        return float(np.sum(cf / ((1.0 + r) ** periods)))

    def fprime(r):
        periods = np.arange(len(cf))
        return float(np.sum(-periods * cf / ((1.0 + r) ** (periods + 1))))

    r = guess
    for _ in range(maxiter):
        try:
            fr = f(r)
            if abs(fr) < tol:
                return float(r)
            fpr = fprime(r)
            if abs(fpr) < 1e-12:
                break
            r_new = r - fr / fpr
            if r_new <= -0.999999:
                break
            r = r_new
        except Exception:
            break

    # fallback bisection scan
    lows = np.concatenate([np.linspace(-0.9999, -0.1, 200), np.linspace(-0.05, 5.0, 2000)])
    vals = [f(x) for x in lows]
    sign_changes = []
    for i in range(len(vals) - 1):
        if vals[i] == 0:
            return float(lows[i])
        if vals[i] * vals[i + 1] < 0:
            sign_changes.append((lows[i], lows[i + 1]))
    if not sign_changes:
        return None
    a, b = sign_changes[0]
    fa, fb = f(a), f(b)
    for _ in range(100):
        m = (a + b) / 2.0
        fm = f(m)
        if abs(fm) < tol:
            return float(m)
        if fa * fm < 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
    return float((a + b) / 2.0)

# ---------------------------
# B/C ratio (benefits / costs)
# ---------------------------
def benefit_cost_ratio(cashflows: List[float], rate: float) -> float:
    benefits = [cf if cf > 0 else 0.0 for cf in cashflows]
    costs = [-cf if cf < 0 else 0.0 for cf in cashflows]
    pv_b = npv(rate, benefits)
    pv_c = npv(rate, costs)
    if abs(pv_c) < 1e-12:
        return None
    return float(pv_b / pv_c)

# ---------------------------   
# Gradientes
# ---------------------------
def gradient_arithmetic(f0: float, g: float, n: int) -> List[float]:
    """Serie aritmética: f0, f0+g, f0+2g, ... (n términos)."""
    return [float(f0 + g * i) for i in range(n)]

def gradient_geometric(f0: float, g: float, n: int) -> List[float]:
    """Serie geométrica: f0, f0(1+g), f0(1+g)^2, ... (n términos)."""
    return [float(f0 * ((1.0 + g) ** i)) for i in range(n)]

# ---------------------------
# Perfil de VAN en una grilla de TMAR
# ---------------------------
def npv_profile(cashflows: List[float], tmar_grid: List[float]) -> List[Tuple[float, float]]:
    """Devuelve lista de (tmar, van)"""
    return [(float(t), npv(t, cashflows)) for t in tmar_grid]

# ---------------------------
# Monte Carlo NPV (riesgo)
# ---------------------------
def monte_carlo_npv(cashflows: List[float], rate: float, n_sim: int = 2000, sigma: float = 0.15, seed: int = None) -> Dict[str, Any]:
    """
    Simula incertidumbre multiplicativa en los flujos (excluye t=0).
    sigma: desviación relativa (p.ej. 0.15 = 15%)
    Retorna percentiles y la distribución (resumida).
    """
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)

    base = np.array(cashflows, dtype=float)
    sims = []
    for _ in range(n_sim):
        shocks = np.ones_like(base)
        # no perturbar inversión inicial (t=0)
        if len(base) > 1:
            shocks[1:] = np.random.normal(1.0, sigma, size=len(base)-1)
        scenario = base * shocks
        sims.append(npv(rate, scenario))

    sims = np.array(sims)
    return {
        "n_sim": n_sim,
        "mean": float(sims.mean()),
        "std": float(sims.std()),
        "p5": float(np.percentile(sims, 5)),
        "p25": float(np.percentile(sims, 25)),
        "p50": float(np.percentile(sims, 50)),
        "p75": float(np.percentile(sims, 75)),
        "p95": float(np.percentile(sims, 95)),
        "samples": sims  # cuidado: puede ser grande
    }

# ---------------------------
# API de evaluación (útil para UI)
# ---------------------------
def evaluate_project(cashflows: List[float], tmar: float, montecarlo: bool = False, mc_nsim: int = 1000, mc_sigma: float = 0.15, mc_seed: int = None) -> Dict[str, Any]:
    """
    Evalúa un proyecto y retorna métricas y análisis extra (perfil, MC opcional).
    """
    van_val = npv(tmar, cashflows)
    tir_val = irr(cashflows)
    bc_val = benefit_cost_ratio(cashflows, tmar)

    out = {
        "cashflows": [float(x) for x in cashflows],
        "tmar": float(tmar),
        "van": float(van_val),
        "tir": float(tir_val) if tir_val is not None else None,
        "b_c": float(bc_val) if bc_val is not None else None
    }

    # perfil VAN (TMAR entorno)
    tgrid = list(np.linspace(max(0.0, tmar - 0.2), tmar + 0.2, 41))
    out["npv_profile"] = npv_profile(cashflows, tgrid)

    if montecarlo:
        mc = monte_carlo_npv(cashflows, tmar, n_sim=mc_nsim, sigma=mc_sigma, seed=mc_seed)
        out["montecarlo"] = mc

    return out

# ---------------------------
# Comparación multicriterio simple
# ---------------------------
def compare_projects(projects: List[Dict[str, Any]], weights: Dict[str, float] = None) -> List[Dict[str, Any]]:
    """
    projects: lista de dicts con keys 'name' y 'metrics' donde metrics contiene 'van','tir','b_c'
    weights: dict con peso para 'van','tir','b_c' (suman 1.0)
    Retorna lista con score normalizado.
    """
    if weights is None:
        weights = {"van": 0.5, "tir": 0.3, "b_c": 0.2}

    # recoger valores
    vans = np.array([p["metrics"].get("van", 0) or 0 for p in projects], dtype=float)
    tirs = np.array([p["metrics"].get("tir", 0) or 0 for p in projects], dtype=float)
    bcs  = np.array([p["metrics"].get("b_c", 0) or 0 for p in projects], dtype=float)

    # normalizar (min-max)
    def safe_normalize(arr):
        if arr.max() == arr.min():
            return np.zeros_like(arr)
        return (arr - arr.min()) / (arr.max() - arr.min())

    nv = safe_normalize(vans)
    nt = safe_normalize(tirs)
    nb = safe_normalize(bcs)

    scores = []
    for i, p in enumerate(projects):
        score = weights.get("van", 0) * nv[i] + weights.get("tir", 0) * nt[i] + weights.get("b_c", 0) * nb[i]
        scores.append({
            "name": p.get("name", f"proj_{i}"),
            "van": float(vans[i]),
            "tir": float(tirs[i]),
            "b_c": float(bcs[i]),
            "score": float(score)
        })

    # ordenar descendente por score
    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores
