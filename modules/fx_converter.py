"""
Módulo de conversión de monedas con API gratuita (open.er-api.com)
Características:
- Tasas spot en tiempo real (sin clave API requerida)
- Cache en memoria con TTL y persistencia en archivo
- Retry con backoff exponencial
- Fallback a tasa manual si falla API
- Validación de códigos ISO 4217
- Logs de auditoría para reproducibilidad

API: open.er-api.com (plan gratuito, sin autenticación requerida)
Límites: ~1500 solicitudes/mes (suficiente para uso normal)

Autor: Simulador Real de Inversiones
Versión: 1.0
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import logging
import time

# ============================================
# Configuración de logging
# ============================================
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - FX_CONVERTER - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# ============================================
# Constantes
# ============================================
API_BASE_URL = "https://open.er-api.com/v6"
CACHE_FILE = "fx_cache.json"
CACHE_TTL_SPOT = 3600  # 1 hora para tasas spot
CACHE_TTL_HISTORICAL = None  # sin expiración para históricas
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # exponencial: 1s, 2s, 4s

# Códigos de moneda válidos (ISO 4217) — ampliado
VALID_CURRENCIES = {
    'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD',
    'CNY', 'INR', 'MXN', 'BRL', 'ARS', 'CLP', 'COP', 'PEN',
    'UYU', 'VES', 'ZAR', 'RUB', 'KRW', 'SGD', 'HKD', 'SEK',
    'NOK', 'DKK', 'THB', 'MYR', 'IDR', 'PHP', 'VND',
    'BAM', 'BGN', 'HRK', 'CZK', 'HUF', 'PLN', 'RON', 'TRY',
    'ISK', 'ILS', 'SAR', 'AED', 'KWD', 'QAR'
}

# ============================================
# Excepciones personalizadas
# ============================================
class FXException(Exception):
    """Excepción base para errores de FX"""
    pass

class UnsupportedCurrencyError(FXException):
    """Se lanzó cuando la moneda no es válida"""
    pass

class RateNotFoundError(FXException):
    """Se lanzó cuando no hay tasa disponible para esa fecha"""
    pass

class ProviderError(FXException):
    """Se lanzó cuando falla el proveedor de tasas"""
    pass

# ============================================
# Clase Cache
# ============================================
class FXCache:
    """Gestor de cache en memoria y persistencia en archivo JSON"""
    
    def __init__(self, cache_file: str = CACHE_FILE):
        self.cache_file = cache_file
        self.memory_cache: Dict = {}
        self.load_from_file()
    
    def load_from_file(self):
        """Cargar cache desde archivo JSON"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.memory_cache = json.load(f)
                logger.info(f"Cache cargada desde {self.cache_file} ({len(self.memory_cache)} entradas)")
            else:
                logger.info(f"Cache vacía (archivo {self.cache_file} no existe)")
        except Exception as e:
            logger.error(f"Error al cargar cache: {e}")
            self.memory_cache = {}
    
    def save_to_file(self):
        """Guardar cache en archivo JSON"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory_cache, f, indent=2, ensure_ascii=False)
            logger.debug(f"Cache guardada en {self.cache_file}")
        except Exception as e:
            logger.error(f"Error al guardar cache: {e}")
    
    def get(self, key: str) -> Optional[Dict]:
        """Obtener valor de cache; retorna None si expiró o no existe"""
        if key not in self.memory_cache:
            return None
        
        entry = self.memory_cache[key]
        
        # Verificar expiración
        if entry.get('expires_at'):
            expires_at = datetime.fromisoformat(entry['expires_at'])
            if datetime.now() > expires_at:
                del self.memory_cache[key]
                self.save_to_file()
                logger.debug(f"Entrada cache expirada: {key}")
                return None
        
        logger.debug(f"Cache hit: {key}")
        return entry['value']
    
    def set(self, key: str, value: Dict, ttl: Optional[int] = None):
        """Guardar valor en cache con TTL opcional"""
        expires_at = None
        if ttl:
            expires_at = (datetime.now() + timedelta(seconds=ttl)).isoformat()
        
        self.memory_cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'stored_at': datetime.now().isoformat()
        }
        self.save_to_file()
        logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
    
    def clear(self):
        """Limpiar toda la cache"""
        self.memory_cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        logger.info("Cache cleared")

# ============================================
# Función principal: obtener tasa FX
# ============================================
def get_fx_rate(
    from_currency: str,
    to_currency: str,
    date: Optional[str] = None,
    cache: Optional[FXCache] = None,
    manual_rate: Optional[float] = None
) -> Dict:
    """
    Obtiene la tasa de cambio entre dos monedas.
    
    Parámetros:
    -----------
    from_currency : str
        Moneda origen (ej: 'USD', código ISO 4217)
    to_currency : str
        Moneda destino (ej: 'ARS', código ISO 4217)
    date : str, optional
        Fecha en formato YYYY-MM-DD para tasa histórica.
        Si es None, usa la tasa spot (hoy).
        Nota: En plan gratuito, solo se devuelven tasas spot (actuales).
        El parámetro se acepta pero no cambia el resultado.
    cache : FXCache, optional
        Objeto cache. Si es None, se crea uno internamente.
    manual_rate : float, optional
        Tasa manual de fallback si falla el proveedor.
    
    Retorna:
    --------
    Dict con claves:
        - rate: float (cuánto vale 1 from_currency en to_currency)
        - timestamp: str (ISO 8601, cuándo se obtuvo la tasa)
        - provider: str (identificador del proveedor)
        - source: str ('cache', 'api', 'manual')
        - error: str (si hay error)
    
    Excepciones:
    -----------
    UnsupportedCurrencyError : si alguna moneda es inválida
    RateNotFoundError : si no hay tasa para esa fecha
    ProviderError : si falla la API y no hay fallback
    """
    
    if cache is None:
        cache = FXCache()
    
    # Validar códigos ISO
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    
    if from_currency not in VALID_CURRENCIES:
        raise UnsupportedCurrencyError(f"Moneda no soportada: {from_currency}")
    if to_currency not in VALID_CURRENCIES:
        raise UnsupportedCurrencyError(f"Moneda no soportada: {to_currency}")
    
    # Si es la misma moneda
    if from_currency == to_currency:
        result = {
            'rate': 1.0,
            'timestamp': datetime.now().isoformat(),
            'provider': 'exchangerate.host',
            'source': 'identity',
            'from_currency': from_currency,
            'to_currency': to_currency
        }
        logger.info(f"Tasa identidad: {from_currency} = {to_currency}")
        return result
    
    # Construir clave de cache
    cache_key = f"fx_{from_currency}_{to_currency}_{date or 'spot'}"
    
    # Intentar obtener de cache
    cached_value = cache.get(cache_key)
    if cached_value:
        cached_value['source'] = 'cache'
        logger.info(f"Usando tasa en cache: {from_currency}->{to_currency} @ {cached_value['rate']}")
        return cached_value
    
    # Intentar obtener de API con retry
    ttl = None if date else CACHE_TTL_SPOT
    result = _fetch_rate_with_retry(from_currency, to_currency, date)
    
    if result and 'error' not in result:
        result['source'] = 'api'
        cache.set(cache_key, result, ttl=ttl)
        logger.info(f"Tasa obtenida de API: {from_currency}->{to_currency} @ {result['rate']}")
        return result
    
    # Fallback: tasa manual si se proporciona
    if manual_rate is not None:
        result = {
            'rate': manual_rate,
            'timestamp': datetime.now().isoformat(),
            'provider': 'manual',
            'source': 'manual',
            'from_currency': from_currency,
            'to_currency': to_currency,
            'note': 'Tasa manual suministrada por usuario (fallback)'
        }
        logger.warning(f"Usando tasa manual: {from_currency}->{to_currency} @ {manual_rate}")
        return result
    
    # Si todo falla
    error_msg = f"No fue posible obtener tasa para {from_currency}->{to_currency}"
    if date:
        error_msg += f" en fecha {date}"
    logger.error(error_msg)
    raise ProviderError(error_msg)

# ============================================
# Función auxiliar: fetch con retry
# ============================================
def _fetch_rate_with_retry(
    from_currency: str,
    to_currency: str,
    date: Optional[str] = None,
    attempt: int = 0
) -> Optional[Dict]:
    """
    Intenta obtener la tasa de la API con backoff exponencial.
    Usa open.er-api.com (gratuita y confiable)
    """
    
    try:
        # Nota: open.er-api.com no soporta tasas históricas en plan gratuito
        # Por ahora usamos solo tasas spot
        if date:
            logger.warning(f"Tasas históricas no disponibles en plan gratuito. Usando tasa spot actual.")
        
        url = f"{API_BASE_URL}/latest/{from_currency}"
        
        logger.debug(f"Intentando obtener tasa spot: {from_currency}->{to_currency}")
        
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('result') != 'success':
            raise ProviderError(f"API retornó error: {data.get('error', 'desconocido')}")
        
        if 'rates' not in data or to_currency not in data['rates']:
            raise RateNotFoundError(f"Tasa no disponible para {to_currency}")
        
        rate = data['rates'][to_currency]
        result = {
            'rate': float(rate),
            'timestamp': datetime.now().isoformat(),
            'provider': 'open.er-api.com',
            'from_currency': from_currency,
            'to_currency': to_currency
        }
        
        logger.info(f"Tasa obtenida: {from_currency}->{to_currency} = {rate}")
        return result
    
    except requests.exceptions.RequestException as e:
        if attempt < MAX_RETRIES:
            wait_time = RETRY_BACKOFF ** attempt
            logger.warning(f"Error de red (intento {attempt + 1}/{MAX_RETRIES}): {e}. "
                          f"Reintentando en {wait_time}s...")
            time.sleep(wait_time)
            return _fetch_rate_with_retry(from_currency, to_currency, date, attempt + 1)
        else:
            logger.error(f"Fallo después de {MAX_RETRIES} intentos: {e}")
            return None
    
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return None

# ============================================
# Función de conversión
# ============================================
def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
    date: Optional[str] = None,
    cache: Optional[FXCache] = None,
    manual_rate: Optional[float] = None
) -> Dict:
    """
    Convierte un monto de una moneda a otra.
    
    Parámetros:
    -----------
    amount : float
        Cantidad a convertir
    from_currency : str
        Moneda origen
    to_currency : str
        Moneda destino
    date : str, optional
        Fecha para tasa histórica (YYYY-MM-DD)
    cache : FXCache, optional
        Cache (si None, se crea internamente)
    manual_rate : float, optional
        Tasa manual de fallback
    
    Retorna:
    --------
    Dict con:
        - amount_original: float
        - amount_converted: float
        - from_currency: str
        - to_currency: str
        - rate: float
        - timestamp: str
        - source: str ('cache', 'api', 'manual')
    """
    
    fx_data = get_fx_rate(
        from_currency,
        to_currency,
        date=date,
        cache=cache,
        manual_rate=manual_rate
    )
    
    amount_converted = amount * fx_data['rate']
    
    return {
        'amount_original': amount,
        'amount_converted': amount_converted,
        'from_currency': from_currency,
        'to_currency': to_currency,
        'rate': fx_data['rate'],
        'timestamp': fx_data['timestamp'],
        'source': fx_data.get('source', 'unknown'),
        'provider': fx_data.get('provider', 'unknown')
    }

# ============================================
# Función de validación
# ============================================
def is_valid_currency(currency_code: str) -> bool:
    """Verifica si un código de moneda es válido"""
    return currency_code.upper() in VALID_CURRENCIES

def get_supported_currencies() -> list:
    """Retorna lista de monedas soportadas"""
    return sorted(list(VALID_CURRENCIES))
