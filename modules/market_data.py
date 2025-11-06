"""
Módulo de integración con Yahoo Finance para datos reales de mercado.
Permite comparar simulaciones con performance real de acciones.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import streamlit as st


def get_stock_info(ticker: str) -> Optional[Dict]:
    """
    Obtiene información básica de una acción.
    
    Args:
        ticker: Símbolo del ticker (ej: "AAPL", "MSFT")
    
    Returns:
        Dict con información de la acción o None si no se encuentra
    """
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info
        
        if not info or 'symbol' not in info:
            return None
        
        return {
            "symbol": info.get("symbol", ticker.upper()),
            "name": info.get("longName", info.get("shortName", ticker.upper())),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap", 0),
            "current_price": info.get("currentPrice", info.get("regularMarketPrice", 0)),
            "currency": info.get("currency", "USD"),
            "dividend_yield": info.get("dividendYield", 0),
            "pe_ratio": info.get("trailingPE", 0),
            "52w_high": info.get("fiftyTwoWeekHigh", 0),
            "52w_low": info.get("fiftyTwoWeekLow", 0),
        }
    except Exception as e:
        st.error(f"Error obteniendo datos de {ticker}: {str(e)}")
        return None


def get_historical_data(ticker: str, years: int = 5) -> Optional[pd.DataFrame]:
    """
    Obtiene datos históricos de una acción.
    
    Args:
        ticker: Símbolo del ticker
        years: Años de historial a obtener
    
    Returns:
        DataFrame con precios históricos o None si falla
    """
    try:
        stock = yf.Ticker(ticker.upper())
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years*365)
        
        hist = stock.history(start=start_date, end=end_date)
        
        if hist.empty:
            return None
        
        return hist
    except Exception as e:
        st.error(f"Error obteniendo histórico de {ticker}: {str(e)}")
        return None


def calculate_cagr(ticker: str, years: int = 5) -> Optional[float]:
    """
    Calcula el CAGR (Compound Annual Growth Rate) de una acción.
    
    Args:
        ticker: Símbolo del ticker
        years: Años para calcular el CAGR
    
    Returns:
        CAGR en porcentaje o None si falla
    """
    hist = get_historical_data(ticker, years)
    
    if hist is None or len(hist) < 2:
        return None
    
    try:
        start_price = hist['Close'].iloc[0]
        end_price = hist['Close'].iloc[-1]
        
        # Calcular años reales basados en fechas
        actual_years = (hist.index[-1] - hist.index[0]).days / 365.25
        
        if start_price <= 0 or actual_years <= 0:
            return None
        
        cagr = ((end_price / start_price) ** (1 / actual_years) - 1) * 100
        return round(cagr, 2)
    except Exception as e:
        st.error(f"Error calculando CAGR: {str(e)}")
        return None


def calculate_volatility(ticker: str, years: int = 5) -> Optional[float]:
    """
    Calcula la volatilidad (desviación estándar anualizada) de una acción.
    
    Args:
        ticker: Símbolo del ticker
        years: Años de datos a usar
    
    Returns:
        Volatilidad en porcentaje o None si falla
    """
    hist = get_historical_data(ticker, years)
    
    if hist is None or len(hist) < 2:
        return None
    
    try:
        # Calcular retornos diarios
        daily_returns = hist['Close'].pct_change().dropna()
        
        # Volatilidad anualizada (252 días de trading)
        volatility = daily_returns.std() * np.sqrt(252) * 100
        return round(volatility, 2)
    except Exception as e:
        st.error(f"Error calculando volatilidad: {str(e)}")
        return None


def compare_simulation_vs_real(
    simulation_tea: float,
    simulation_years: int,
    simulation_initial: float,
    ticker: str,
    simulation_fv_total: float = None
) -> Optional[Dict]:
    """
    Compara una simulación con el performance real de una acción.
    
    IMPORTANTE: Esta comparación es REFERENCIAL porque:
    - La simulación puede incluir aportes periódicos
    - Las acciones tienen volatilidad (riesgo) vs. instrumentos de renta fija
    - Los datos históricos NO garantizan rendimientos futuros
    
    Args:
        simulation_tea: TEA de la simulación (%)
        simulation_years: Años de la simulación
        simulation_initial: Inversión inicial
        ticker: Símbolo del ticker a comparar
        simulation_fv_total: Valor futuro total de la simulación (opcional)
    
    Returns:
        Dict con comparación o None si falla
    """
    # Obtener CAGR real del mercado
    real_cagr = calculate_cagr(ticker, simulation_years)
    
    if real_cagr is None:
        return None
    
    # Calcular valor final SI se hubiera invertido en la acción real
    # (solo inversión inicial, sin aportes periódicos)
    real_final_value = simulation_initial * ((1 + real_cagr/100) ** simulation_years)
    
    # Usar el FV total de la simulación si se proporciona, sino calcularlo simple
    if simulation_fv_total is not None:
        sim_final_value = simulation_fv_total
    else:
        sim_final_value = simulation_initial * ((1 + simulation_tea/100) ** simulation_years)
    
    # Diferencia
    difference = real_final_value - sim_final_value
    difference_pct = ((real_final_value / sim_final_value) - 1) * 100 if sim_final_value > 0 else 0
    
    # Evaluación comparativa
    if simulation_tea > real_cagr + 2:
        evaluation = "optimista"
        message = f"Tu TEA proyectado ({simulation_tea:.2f}%) es significativamente mayor que el CAGR histórico de {ticker} ({real_cagr:.2f}%)"
    elif simulation_tea < real_cagr - 2:
        evaluation = "conservadora"
        message = f"Tu TEA proyectado ({simulation_tea:.2f}%) es menor que el CAGR histórico de {ticker} ({real_cagr:.2f}%)"
    else:
        evaluation = "realista"
        message = f"Tu TEA proyectado ({simulation_tea:.2f}%) está alineado con el CAGR histórico de {ticker} ({real_cagr:.2f}%)"
    
    return {
        "ticker": ticker,
        "simulation_tea": simulation_tea,
        "real_cagr": real_cagr,
        "simulation_final": sim_final_value,
        "real_final": real_final_value,
        "difference": difference,
        "difference_pct": difference_pct,
        "evaluation": evaluation,
        "message": message,
        "has_periodic_contributions": simulation_fv_total is not None
    }


def search_tickers_by_return(
    target_return: float,
    tolerance: float = 2.0,
    years: int = 5,
    tickers: List[str] = None
) -> List[Dict]:
    """
    Busca tickers que han dado un retorno similar al objetivo.
    
    Args:
        target_return: Retorno objetivo en % anual
        tolerance: Tolerancia en puntos porcentuales
        years: Años de histórico a evaluar
        tickers: Lista de tickers a evaluar (si None, usa una lista predefinida)
    
    Returns:
        Lista de tickers que cumplen el criterio
    """
    if tickers is None:
        # Tickers populares de S&P 500
        tickers = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
            "JPM", "JNJ", "V", "PG", "MA", "HD", "DIS", "NFLX", "PYPL", "INTC",
            "VZ", "T", "KO", "PFE", "MRK", "WMT", "BAC", "XOM", "CVX"
        ]
    
    matches = []
    
    for ticker in tickers:
        try:
            cagr = calculate_cagr(ticker, years)
            if cagr is not None:
                if abs(cagr - target_return) <= tolerance:
                    info = get_stock_info(ticker)
                    if info:
                        matches.append({
                            "ticker": ticker,
                            "name": info["name"],
                            "cagr": cagr,
                            "difference": abs(cagr - target_return)
                        })
        except:
            continue
    
    # Ordenar por menor diferencia
    matches.sort(key=lambda x: x["difference"])
    return matches


def get_comparative_chart_data(
    ticker: str,
    initial_investment: float,
    tea_annual: float,
    years: int
) -> Optional[pd.DataFrame]:
    """
    Genera datos para gráfico comparativo: simulación vs realidad.
    
    Args:
        ticker: Símbolo del ticker
        initial_investment: Inversión inicial
        tea_annual: TEA de la simulación
        years: Años a proyectar
    
    Returns:
        DataFrame con datos para gráfico o None si falla
    """
    hist = get_historical_data(ticker, years)
    
    if hist is None or len(hist) < 2:
        return None
    
    try:
        # Normalizar precios históricos a la inversión inicial
        start_price = hist['Close'].iloc[0]
        hist['Portfolio_Value'] = (hist['Close'] / start_price) * initial_investment
        
        # Crear proyección de simulación
        dates = pd.date_range(start=hist.index[0], end=hist.index[-1], freq='D')
        sim_data = []
        
        for i, date in enumerate(dates):
            years_elapsed = i / 365.25
            value = initial_investment * ((1 + tea_annual/100) ** years_elapsed)
            sim_data.append({"Date": date, "Simulation": value})
        
        sim_df = pd.DataFrame(sim_data).set_index("Date")
        
        # Combinar
        combined = hist[['Portfolio_Value']].join(sim_df, how='outer')
        combined = combined.interpolate()
        
        return combined
    except Exception as e:
        st.error(f"Error generando datos comparativos: {str(e)}")
        return None


def format_market_cap(market_cap: float) -> str:
    """Formatea capitalización de mercado."""
    if market_cap >= 1e12:
        return f"${market_cap/1e12:.2f}T"
    elif market_cap >= 1e9:
        return f"${market_cap/1e9:.2f}B"
    elif market_cap >= 1e6:
        return f"${market_cap/1e6:.2f}M"
    else:
        return f"${market_cap:,.0f}"


def validate_ticker(ticker: str) -> Tuple[bool, str]:
    """
    Valida si un ticker existe.
    
    Returns:
        Tuple (es_válido, mensaje)
    """
    if not ticker or len(ticker.strip()) == 0:
        return False, "Por favor ingresa un ticker"
    
    info = get_stock_info(ticker)
    
    if info is None:
        return False, f"No se encontró el ticker '{ticker.upper()}'"
    
    return True, f"✅ {info['name']} ({info['symbol']})"
