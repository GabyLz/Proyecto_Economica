"""
Presets / Plantillas predefinidas para simulaciones rápidas
"""

PRESETS_ACCIONES = {
    "conservador": {
        "nombre": "🏦 Conservador",
        "descripcion": "Bajo riesgo, retorno modesto",
        "initial": 10000,
        "annuity": 500,
        "modality": "Mensual",
        "years": 10,
        "tea_pct": 5.0,
        "bolsa": "SPL",
        "dividend_pct": 3.0,
    },
    "balanceado": {
        "nombre": "📊 Balanceado",
        "descripcion": "Riesgo medio, retorno equilibrado",
        "initial": 15000,
        "annuity": 1000,
        "modality": "Mensual",
        "years": 15,
        "tea_pct": 10.0,
        "bolsa": "SPL",
        "dividend_pct": 5.0,
    },
    "agresivo": {
        "nombre": "🚀 Agresivo",
        "descripcion": "Alto riesgo, retorno potencial alto",
        "initial": 20000,
        "annuity": 2000,
        "modality": "Mensual",
        "years": 20,
        "tea_pct": 15.0,
        "bolsa": "iBVL",
        "dividend_pct": 2.0,
    },
}

PRESETS_BONOS = {
    "bonos_seguros": {
        "nombre": "💼 Bono Seguro (BBB+)",
        "descripcion": "Bajo riesgo, cupón moderado",
        "face_value": 100000,
        "coupon_rate": 6.0,
        "tea_yield": 5.5,
        "period": "Semestral",
        "n_periods": 20,
        "years": 10,
    },
    "bonos_rentables": {
        "nombre": "📈 Bono Rentable (A)",
        "descripcion": "Riesgo moderado, buen cupón",
        "face_value": 100000,
        "coupon_rate": 8.0,
        "tea_yield": 7.5,
        "period": "Semestral",
        "n_periods": 20,
        "years": 10,
    },
    "bonos_emergentes": {
        "nombre": "🌍 Bono Emergente (BB)",
        "descripcion": "Mayor riesgo, cupón alto",
        "face_value": 100000,
        "coupon_rate": 10.0,
        "tea_yield": 9.5,
        "period": "Semestral",
        "n_periods": 20,
        "years": 10,
    },
}


def get_preset_acciones(preset_name: str):
    """Retorna preset de acciones por nombre"""
    return PRESETS_ACCIONES.get(preset_name, None)


def get_preset_bonos(preset_name: str):
    """Retorna preset de bonos por nombre"""
    return PRESETS_BONOS.get(preset_name, None)


def list_presets_acciones():
    """Retorna lista de presets disponibles para acciones"""
    return [(k, v["nombre"]) for k, v in PRESETS_ACCIONES.items()]


def list_presets_bonos():
    """Retorna lista de presets disponibles para bonos"""
    return [(k, v["nombre"]) for k, v in PRESETS_BONOS.items()]
