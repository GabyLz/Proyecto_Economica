"""
Módulo de comparación de bonos con mercado real
"""

from typing import Dict, List, Tuple

# TASAS DE REFERENCIA (se actualizan periódicamente)
# Última actualización: Noviembre 2025

BOND_COMPARABLES = {
    "treasury_us_10y": {
        "name": "🇺🇸 Tesoro USA 10Y",
        "current_yield": 4.5,
        "rating": "AAA",
        "risk_level": "Muy Bajo",
    },
    "treasury_us_5y": {
        "name": "🇺🇸 Tesoro USA 5Y",
        "current_yield": 4.3,
        "rating": "AAA",
        "risk_level": "Muy Bajo",
    },
    "corporate_grade_a": {
        "name": "📊 Corporativo Grado A",
        "current_yield": 7.0,
        "rating": "A",
        "risk_level": "Bajo-Medio",
    },
    "corporate_grade_bbb": {
        "name": "📊 Corporativo Grado BBB",
        "current_yield": 6.5,
        "rating": "BBB",
        "risk_level": "Medio",
    },
    "corporate_highyield": {
        "name": "📈 High Yield Bonds",
        "current_yield": 9.2,
        "rating": "BB-CCC",
        "risk_level": "Alto",
    },
    "emerging_markets": {
        "name": "🌍 Bonos Emergentes",
        "current_yield": 8.5,
        "rating": "BB+",
        "risk_level": "Alto",
    },
    "peru_soberano": {
        "name": "🇵🇪 Bono Soberano Perú",
        "current_yield": 5.2,
        "rating": "BBB-",
        "risk_level": "Medio",
    },
}


def classify_spread(your_tea: float, comparable_yield: float) -> Tuple[str, str]:
    """
    Clasifica un spread como realista/optimista/conservador
    """
    spread = your_tea - comparable_yield
    
    if spread < 2:
        return ("muy_conservador", "✅✅ Muy Conservador")
    elif spread < 3.5:
        return ("conservador", "✅ Conservador")
    elif spread <= 5.5:
        return ("realista", "ℹ️ Realista")
    elif spread < 7:
        return ("optimista", "⚠️ Optimista")
    else:
        return ("muy_optimista", "❌ Muy Optimista")


def get_closest_comparables(your_tea: float, count: int = 3) -> List[Tuple[str, Dict, float]]:
    """
    Retorna los bonos más cercanos en TEA al tuyo
    """
    results = []
    
    for key, bond_data in BOND_COMPARABLES.items():
        diff = abs(your_tea - bond_data["current_yield"])
        results.append((key, bond_data, diff))
    
    results.sort(key=lambda x: x[2])
    return results[:count]


def get_risk_assessment(your_tea: float, your_coupon: float, your_years: int) -> Dict:
    """
    Análisis completo de riesgo/retorno de tu bono
    """
    closest = get_closest_comparables(your_tea, count=5)
    avg_spread = sum(c[1]["current_yield"] for c in closest) / len(closest)
    spread_vs_avg = your_tea - avg_spread
    classification, icon = classify_spread(your_tea, avg_spread)
    
    if your_years < 3:
        plazo_eval = "📌 Corto plazo"
    elif your_years < 7:
        plazo_eval = "📊 Mediano plazo"
    else:
        plazo_eval = "📈 Largo plazo"
    
    if your_coupon < your_tea:
        coupon_eval = "⚠️ Cupón bajo"
    elif your_coupon > your_tea:
        coupon_eval = "✅ Cupón alto"
    else:
        coupon_eval = "ℹ️ Cupón = TEA"
    
    return {
        "spread_vs_comparables": spread_vs_avg,
        "classification": classification,
        "icon": icon,
        "closest_comparables": closest[:3],
        "plazo_evaluation": plazo_eval,
        "coupon_evaluation": coupon_eval,
    }
