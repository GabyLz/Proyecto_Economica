"""
Componente UI para mostrar comparación con datos reales del mercado.
"""

import streamlit as st
import plotly.graph_objects as go
from modules.market_data import (
    get_stock_info,
    calculate_cagr,
    calculate_volatility,
    compare_simulation_vs_real,
    search_tickers_by_return,
    get_comparative_chart_data,
    format_market_cap,
    validate_ticker
)


def show_market_comparison(simulation_tea: float, simulation_years: int, initial_investment: float, fv_total: float = None):
    """
    Muestra sección de comparación con mercado real con diseño mejorado.
    
    Args:
        simulation_tea: TEA de la simulación
        simulation_years: Años de la simulación
        initial_investment: Inversión inicial
        fv_total: Valor futuro total de la simulación (opcional, incluye aportes periódicos)
    """
    st.markdown("---")
    
    # Header elegante con ícono y descripción
    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.markdown("### 📊 Comparación con Mercado Real")
        st.caption("Compara tu proyección con el rendimiento histórico real de acciones")
    with col_header2:
        with st.popover("ℹ️ Ayuda", width='stretch'):
            st.markdown("""
            **¿Qué es esto?**
            
            Comparamos tu TEA proyectado con el CAGR histórico real de acciones del mercado.
            
            **Glosario:**
            - **TEA**: Tasa Efectiva Anual (tu proyección)
            - **CAGR**: Tasa de Crecimiento Anual Compuesta (histórico real)
            - **Volatilidad**: Riesgo - qué tanto varía el precio
            """)
    
    # Advertencia en expander (menos invasivo pero accesible)
    with st.expander("⚠️ **LEE ESTO PRIMERO** - Advertencias Importantes", expanded=False):
        st.error("""
        **Esta comparación es REFERENCIAL y tiene limitaciones:**
        
        1. � Los rendimientos pasados **NO garantizan** resultados futuros
        2. 🎲 Acciones = **Alto riesgo y volatilidad** ≠ Renta fija
        3. � Tu simulación puede incluir aportes periódicos, el CAGR solo considera inversión inicial
        4. 📊 No incluye dividendos reinvertidos, comisiones ni impuestos
        5. ⚖️ **NO es una recomendación de inversión**
        
        👨‍💼 **Consulta con un asesor financiero certificado antes de invertir.**
        """)
    
    # Inicializar session_state para el ticker
    if "market_ticker_to_compare" not in st.session_state:
        st.session_state.market_ticker_to_compare = None
    
    # Input de ticker con diseño limpio
    st.markdown("#### 🔎 Buscar Acción")
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        ticker_input = st.text_input(
            "Ingresa el símbolo (ticker)",
            placeholder="Ej: AAPL, MSFT, GOOGL, TSLA...",
            help="Ticker de la acción en bolsa (generalmente en inglés)",
            key="market_ticker_input",
            label_visibility="collapsed"
        )
    
    with col2:
        if st.button("🔍 Comparar", type="primary", width='stretch', key="compare_market_btn"):
            if ticker_input and ticker_input.strip():
                st.session_state.market_ticker_to_compare = ticker_input.strip().upper()
            else:
                st.error("Ingresa un ticker válido")
    
    with col3:
        if st.button("🗑️ Limpiar", width='stretch', key="clear_market_btn"):
            st.session_state.market_ticker_to_compare = None
            st.rerun()
    
    # Ejemplos rápidos
    st.caption("💡 **Ejemplos populares**: AAPL (Apple), MSFT (Microsoft), GOOGL (Google), AMZN (Amazon), TSLA (Tesla), SPY (S&P 500)")
    
    # Mostrar comparación si hay un ticker guardado
    if st.session_state.market_ticker_to_compare:
        ticker_to_use = st.session_state.market_ticker_to_compare
        
        with st.spinner(f"📡 Obteniendo datos de {ticker_to_use}..."):
            # Validar ticker
            is_valid, message = validate_ticker(ticker_to_use)
            
            if not is_valid:
                st.error(f"❌ {message}")
                st.info("💡 **Tip**: Verifica que el ticker esté escrito correctamente y que la acción cotice en bolsas estadounidenses")
                return
            
            # Obtener info básica
            info = get_stock_info(ticker_to_use)
            
            if info:
                st.markdown("---")
                
                # Card elegante de información de la empresa - obtener tema
                theme = st.session_state.get("current_theme", "Claro (default)")
                
                # Seleccionar gradiente según tema
                if "Verde" in theme:
                    gradient = "linear-gradient(135deg, #059669 0%, #065F46 100%)"
                elif "Azul" in theme:
                    gradient = "linear-gradient(135deg, #2563EB 0%, #1E3A8A 100%)"
                elif "Minimal" in theme:
                    gradient = "linear-gradient(135deg, #525252 0%, #262626 100%)"
                else:  # Claro (default)
                    gradient = "linear-gradient(135deg, #DC2626 0%, #7F1D1D 100%)"
                
                st.markdown(f"""
                <style>
                    .gradient-header-white h1, .gradient-header-white h2, .gradient-header-white p {{
                        color: #FFFFFF !important;
                        -webkit-text-fill-color: #FFFFFF !important;
                    }}
                </style>
                <div class="gradient-header-white" style="background: {gradient}; 
                            padding: 20px; 
                            border-radius: 10px; 
                            margin-bottom: 20px;">
                    <h2 style="color: #FFFFFF !important; margin: 0; font-weight: bold; -webkit-text-fill-color: #FFFFFF !important;">🏢 {info['name']}</h2>
                    <p style="color: #FFFFFF !important; margin: 5px 0 0 0; font-size: 18px; opacity: 0.9; -webkit-text-fill-color: #FFFFFF !important;">Ticker: {info['symbol']} | {info['sector']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Métricas clave en cards
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("💵 Precio Actual", f"${info['current_price']:.2f}", help="Precio de cierre más reciente")
                with c2:
                    st.metric("📊 Capitalización", format_market_cap(info['market_cap']), help="Valor total de mercado")
                with c3:
                    st.metric("💰 Dividendo", f"{info['dividend_yield']*100:.2f}%" if info['dividend_yield'] else "N/A", help="Rentabilidad por dividendo anual")
                with c4:
                    pe_ratio = f"{info['pe_ratio']:.1f}x" if info.get('pe_ratio') else "N/A"
                    st.metric("📈 P/E Ratio", pe_ratio, help="Precio/Ganancia - valoración relativa")
                
                st.markdown("---")
                
                # Comparación
                comparison = compare_simulation_vs_real(
                    simulation_tea,
                    simulation_years,
                    initial_investment,
                    ticker_to_use,
                    simulation_fv_total=fv_total
                )
                
                if comparison:
                    # Tabs para organizar mejor la información
                    tab1, tab2, tab3 = st.tabs(["📊 Comparación", "📈 Proyección Gráfica", "⚠️ Análisis de Riesgo"])
                    
                    with tab1:
                        # NOTA sobre aportes periódicos (más visible)
                        if comparison.get('has_periodic_contributions', False):
                            st.info("""
                            ℹ️ **Nota sobre tu simulación**: Incluye **aportes periódicos**. 
                            La comparación con {ticker} solo considera **inversión inicial única**. 
                            Compara las **tasas** (TEA vs CAGR), no los valores finales directamente.
                            """.format(ticker=info['symbol']))
                        
                        # Resultados de comparación con diseño mejorado
                        st.markdown("#### 🔄 Tu Proyección vs. Realidad Histórica")
                    
                        # Comparación lado a lado con cards elegantes
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            st.markdown("""
                            <div style="background-color: #f0f7ff; padding: 20px; border-radius: 10px; border-left: 5px solid #2196F3;">
                                <h4 style="margin: 0; color: #1976D2;">📈 Tu Simulación</h4>
                            </div>
                            """, unsafe_allow_html=True)
                            st.metric(
                                "Tasa Efectiva Anual (TEA)",
                                f"{comparison['simulation_tea']:.2f}%",
                                help="Tu tasa proyectada en la simulación"
                            )
                            st.metric(
                                "Valor Final Proyectado",
                                f"${comparison['simulation_final']:,.2f}",
                                help="Incluye aportes periódicos si los configuraste"
                            )
                        
                        with col_b:
                            st.markdown(f"""
                            <div style="background-color: #fff4e6; padding: 20px; border-radius: 10px; border-left: 5px solid #FF9800;">
                                <h4 style="margin: 0; color: #F57C00;">📊 {info['symbol']} - Histórico Real</h4>
                            </div>
                            """, unsafe_allow_html=True)
                            st.metric(
                                f"CAGR Histórico ({simulation_years} años)",
                                f"{comparison['real_cagr']:.2f}%",
                                help=f"Rendimiento anual compuesto real de {info['symbol']}"
                            )
                            st.metric(
                                "Valor Final si hubieras invertido",
                                f"${comparison['real_final']:,.2f}",
                                help="Solo inversión inicial, sin aportes adicionales"
                            )
                        
                        # Evaluación visual prominente
                        st.markdown("---")
                        st.markdown("#### 🎯 Evaluación de tu Proyección")
                        
                        diff_pct = comparison['difference_pct']
                        
                        if comparison['evaluation'] == "optimista":
                            st.error(f"""
                            ### ⚠️ Proyección OPTIMISTA
                            
                            Tu TEA proyectado (**{comparison['simulation_tea']:.2f}%**) es **mayor** que el CAGR histórico real de {info['symbol']} (**{comparison['real_cagr']:.2f}%**).
                            
                            **¿Qué significa?** 
                            - Estás esperando un rendimiento superior al histórico
                            - Mayor rendimiento esperado = Mayor riesgo requerido
                            - Considera si tu inversión justifica ese rendimiento
                            
                            **Diferencia**: {abs(diff_pct):.1f}% {'más alto' if diff_pct > 0 else 'más bajo'}
                            """)
                        elif comparison['evaluation'] == "conservadora":
                            st.success(f"""
                            ### ✅ Proyección CONSERVADORA
                            
                            Tu TEA proyectado (**{comparison['simulation_tea']:.2f}%**) es **menor** que el CAGR histórico real de {info['symbol']} (**{comparison['real_cagr']:.2f}%**).
                            
                            **¿Qué significa?**
                            - Estás siendo prudente en tus expectativas
                            - Menor riesgo asumido en tu proyección
                            - Puede haber oportunidades de mejor rendimiento
                            
                            **Diferencia**: {abs(diff_pct):.1f}% {'más alto' if diff_pct > 0 else 'más bajo'}
                            """)
                        else:
                            st.info(f"""
                            ### ℹ️ Proyección REALISTA
                            
                            Tu TEA proyectado (**{comparison['simulation_tea']:.2f}%**) está **alineado** con el CAGR histórico real de {info['symbol']} (**{comparison['real_cagr']:.2f}%**).
                            
                            **¿Qué significa?**
                            - Tu expectativa coincide con datos históricos
                            - Balance razonable entre riesgo y retorno
                            - Recuerda: pasado no garantiza futuro
                            
                            **Diferencia**: {abs(diff_pct):.1f}%
                            """)
                    
                    with tab2:
                        st.markdown("#### 📈 ¿Cómo habría crecido tu inversión?")
                        st.caption(f"Comparación visual: inversión inicial de ${initial_investment:,.2f} durante {simulation_years} años")
                        
                        chart_data = get_comparative_chart_data(
                            ticker_to_use,
                            initial_investment,
                            simulation_tea,
                            simulation_years
                        )
                        
                        if chart_data is not None:
                            fig = go.Figure()
                            
                            # Línea de valor real con estilo mejorado
                            fig.add_trace(go.Scatter(
                                x=chart_data.index,
                                y=chart_data['Portfolio_Value'],
                                mode='lines',
                                name=f'{info["symbol"]} (Histórico Real)',
                                line=dict(color='#FF9800', width=3),
                                fill='tozeroy',
                                fillcolor='rgba(255, 152, 0, 0.1)',
                                hovertemplate='<b>📊 Real</b><br>%{x|%d/%m/%Y}<br>💰 $%{y:,.2f}<extra></extra>'
                            ))
                            
                            # Línea de simulación con estilo mejorado
                            fig.add_trace(go.Scatter(
                                x=chart_data.index,
                                y=chart_data['Simulation'],
                                mode='lines',
                                name='Tu Proyección',
                                line=dict(color='#2196F3', width=3, dash='dash'),
                                hovertemplate='<b>📈 Simulación</b><br>%{x|%d/%m/%Y}<br>💵 $%{y:,.2f}<extra></extra>'
                            ))
                            
                            fig.update_layout(
                                title={
                                    'text': f"<b>Crecimiento: Tu Proyección vs {info['symbol']}</b>",
                                    'x': 0.5,
                                    'xanchor': 'center'
                                },
                                xaxis_title="📅 Tiempo",
                                yaxis_title="💰 Valor del Portfolio",
                                hovermode='x unified',
                                template='plotly_white',
                                height=500,
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=1.02,
                                    xanchor="right",
                                    x=1
                                ),
                                plot_bgcolor='rgba(240, 240, 240, 0.5)'
                            )
                            
                            st.plotly_chart(fig, width='stretch')
                            
                            # Explicación del gráfico
                            with st.expander("📖 ¿Cómo leer este gráfico?"):
                                st.markdown(f"""
                                **Línea Naranja Sólida** 🟠: El valor **real** que habría tenido tu inversión en {info['symbol']}
                                
                                **Línea Azul Punteada** 🔵: Tu **proyección** con el TEA que simulaste
                                
                                - Si la línea azul está **arriba**: Tu proyección es más optimista que la realidad histórica
                                - Si la línea azul está **abajo**: Tu proyección es más conservadora
                                - Si están **juntas**: Tu proyección es realista comparada con el histórico
                                
                                ⚠️ **Importante**: Esto es solo referencia histórica, **no predice el futuro**.
                                """)
                        else:
                            st.warning("⚠️ No hay suficientes datos históricos para generar el gráfico")
                    
                    with tab3:
                        st.markdown("#### ⚠️ ¿Qué tan arriesgada es esta acción?")
                        
                        volatility = calculate_volatility(ticker_to_use, simulation_years)
                        if volatility:
                            # Análisis de riesgo visual
                            col_v1, col_v2, col_v3 = st.columns(3)
                            
                            with col_v1:
                                st.metric(
                                    "📉 Volatilidad Anual", 
                                    f"{volatility:.2f}%", 
                                    help="Mide qué tanto varía el precio. Mayor volatilidad = Mayor riesgo"
                                )
                            
                            with col_v2:
                                if volatility < 15:
                                    risk_level = "🟢 Baja"
                                    risk_color = "green"
                                elif volatility < 25:
                                    risk_level = "🟡 Media"
                                    risk_color = "orange"
                                else:
                                    risk_level = "🔴 Alta"
                                    risk_color = "red"
                                
                                st.metric("⚠️ Nivel de Riesgo", risk_level)
                            
                            with col_v3:
                                st.metric(
                                    "📊 CAGR / Volatilidad",
                                    f"{(comparison['real_cagr'] / volatility):.2f}",
                                    help="Ratio rendimiento/riesgo. Mayor = Mejor"
                                )
                            
                            # Interpretación visual
                            st.markdown("---")
                            st.markdown("##### � ¿Qué significa la volatilidad?")
                            
                            if volatility < 15:
                                st.success(f"""
                                **🟢 Volatilidad BAJA ({volatility:.1f}%)**
                                
                                {info['symbol']} tiene movimientos de precio **relativamente estables**.
                                
                                ✅ **Ventajas**: Menos fluctuaciones, más predecible
                                ⚠️ **Desventajas**: Puede limitar ganancias en mercados alcistas
                                
                                **Perfil**: Inversionistas conservadores o de largo plazo
                                """)
                            elif volatility < 25:
                                st.warning(f"""
                                **🟡 Volatilidad MEDIA ({volatility:.1f}%)**
                                
                                {info['symbol']} tiene movimientos de precio **moderados**.
                                
                                ⚖️ **Balance**: Entre estabilidad y potencial de crecimiento
                                ⚠️ **Considera**: Tu tolerancia al riesgo y horizonte de inversión
                                
                                **Perfil**: Inversionistas moderados con visión de mediano plazo
                                """)
                            else:
                                st.error(f"""
                                **🔴 Volatilidad ALTA ({volatility:.1f}%)**
                                
                                {info['symbol']} tiene movimientos de precio **muy variables**.
                                
                                ⚠️ **Riesgo alto**: Puede subir o bajar significativamente
                                💰 **Alto potencial**: Mayor riesgo puede significar mayor retorno
                                
                                **Perfil**: Inversionistas agresivos con alta tolerancia al riesgo
                                """)
                            
                            # Comparación con benchmark
                            st.markdown("---")
                            st.markdown("##### 📊 Contexto de Mercado")
                            
                            col_bench1, col_bench2 = st.columns(2)
                            with col_bench1:
                                st.info("""
                                **Referencia de Volatilidad:**
                                - 🟢 < 15%: Acciones estables (utilities, consumer staples)
                                - 🟡 15-25%: Mercado general (S&P 500 ~18%)
                                - 🔴 > 25%: Acciones de alto riesgo (tech, crypto)
                                """)
                            
                            with col_bench2:
                                risk_return = comparison['real_cagr'] / volatility if volatility > 0 else 0
                                st.metric(
                                    "🎯 Ratio Sharpe Simplificado",
                                    f"{risk_return:.2f}",
                                    help="Rendimiento por unidad de riesgo. >1.0 es bueno"
                                )
                                if risk_return > 1.0:
                                    st.caption("✅ Buen rendimiento ajustado por riesgo")
                                elif risk_return > 0.5:
                                    st.caption("⚖️ Rendimiento moderado vs riesgo")
                                else:
                                    st.caption("⚠️ Alto riesgo para el rendimiento obtenido")
                        else:
                            st.error("No se pudo calcular la volatilidad para este ticker")
                
                else:
                    st.error(f"❌ No se pudo comparar con {ticker_to_use}. Puede que no tenga suficiente historial de datos.")
                    st.info("💡 **Tip**: Prueba con acciones más establecidas como AAPL, MSFT, GOOGL que tienen más años de datos históricos")
    
    # Acciones similares en la parte inferior, más compacto
    if st.session_state.market_ticker_to_compare:
        st.markdown("---")
        with st.expander("🔍 Buscar Acciones con Rendimiento Similar", expanded=False):
            st.caption(f"Encuentra otras acciones con CAGR cercano a tu TEA proyectado ({simulation_tea:.2f}%)")
            
            if st.button("🎯 Buscar Alternativas", key="find_similar", width='stretch', type="secondary"):
                with st.spinner("🔍 Analizando el mercado..."):
                    matches = search_tickers_by_return(simulation_tea, tolerance=3.0, years=simulation_years)
                    
                    if matches:
                        st.success(f"✅ Encontramos {len(matches)} acciones con rendimientos similares")
                        
                        # Mostrar en tabla
                        import pandas as pd
                        df = pd.DataFrame(matches)
                        df['cagr'] = df['cagr'].apply(lambda x: f"{x:.2f}%")
                        df['difference'] = df['difference'].apply(lambda x: f"{x:.2f}%")
                        df.columns = ['Ticker', 'Nombre', 'CAGR', 'Diferencia']
                        
                        st.dataframe(
                            df,
                            width='stretch',
                            hide_index=True
                        )
                        
                        st.info("💡 **Tip**: Estas acciones han dado rendimientos similares históricamente. Considera diversificar tu portfolio.")
                    else:
                        st.warning("⚠️ No encontramos acciones con rendimiento similar. Intenta ajustar tu TEA o el período de análisis.")
