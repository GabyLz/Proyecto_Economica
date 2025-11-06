"""
Módulo de gestión de histórico de simulaciones.
Sistema de persistencia basado en descarga/carga manual de JSON.
Simple y funcional para Streamlit Cloud.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional
import json


def init_user_session():
    """Inicializa el session state."""
    if "user_simulations" not in st.session_state:
        st.session_state.user_simulations = []
    
    if "user_scenarios" not in st.session_state:
        st.session_state.user_scenarios = []
    
    if "simulation_counter" not in st.session_state:
        st.session_state.simulation_counter = 0
    
    if "auto_download_reminder" not in st.session_state:
        st.session_state.auto_download_reminder = 5


def save_simulation(sim_type: str, params: Dict, results: Dict, auto_save: bool = True):
    """Guarda simulación en session state."""
    init_user_session()
    
    st.session_state.simulation_counter += 1
    
    simulation = {
        "id": st.session_state.simulation_counter,
        "type": sim_type,
        "timestamp": datetime.now().isoformat(),
        "params": params,
        "results": results
    }
    
    st.session_state.user_simulations.append(simulation)
    
    if auto_save:
        st.toast(f"💾 Simulación #{simulation['id']} guardada", icon="✅")
    
    if len(st.session_state.user_simulations) % st.session_state.auto_download_reminder == 0:
        st.warning(f"💡 **Recordatorio**: Llevas {len(st.session_state.user_simulations)} simulaciones. ¡Descarga tu respaldo!")
    
    return simulation


def get_simulations(sim_type: Optional[str] = None, limit: int = 100) -> List[Dict]:
    """Obtiene histórico de simulaciones."""
    init_user_session()
    sims = st.session_state.user_simulations
    if sim_type:
        sims = [s for s in sims if s["type"] == sim_type]
    return sims[-limit:][::-1]


def get_simulation_count() -> int:
    """Retorna número total de simulaciones."""
    init_user_session()
    return len(st.session_state.user_simulations)


def clear_simulations():
    """Limpia histórico."""
    st.session_state.user_simulations = []
    st.session_state.simulation_counter = 0


def export_simulations_json() -> str:
    """Exporta simulaciones a JSON."""
    init_user_session()
    export_data = {
        "export_date": datetime.now().isoformat(),
        "app_version": "1.0",
        "total_simulations": len(st.session_state.user_simulations),
        "simulations": st.session_state.user_simulations,
        "scenarios": st.session_state.user_scenarios
    }
    return json.dumps(export_data, indent=2, ensure_ascii=False)


def import_simulations_json(json_str: str) -> tuple[bool, str]:
    """Importa simulaciones desde JSON."""
    try:
        data = json.loads(json_str)
        if "simulations" not in data:
            return False, "❌ Archivo JSON inválido"
        
        st.session_state.user_simulations = data["simulations"]
        
        if st.session_state.user_simulations:
            max_id = max([s.get("id", 0) for s in st.session_state.user_simulations])
            st.session_state.simulation_counter = max_id
        else:
            st.session_state.simulation_counter = 0
        
        if "scenarios" in data:
            st.session_state.user_scenarios = data.get("scenarios", [])
        
        count = len(st.session_state.user_simulations)
        return True, f"✅ Se cargaron {count} simulaciones"
        
    except json.JSONDecodeError:
        return False, "❌ Error: JSON inválido"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"


# ===========================================
# Funciones para Comparador de Escenarios
# ===========================================

def add_scenario(name: str, params: Dict, results: Dict):
    """
    Agrega un escenario al comparador de la sesión.
    
    Args:
        name: Nombre descriptivo del escenario
        params: Parámetros de la simulación
        results: Resultados calculados
    """
    init_user_session()
    
    scenario = {
        "id": len(st.session_state.user_scenarios) + 1,
        "name": name,
        "timestamp": datetime.now().isoformat(),
        "params": params,
        "results": results
    }
    
    st.session_state.user_scenarios.append(scenario)
    return scenario


def get_scenarios() -> List[Dict]:
    """Obtiene todos los escenarios guardados para comparación."""
    init_user_session()
    return st.session_state.user_scenarios


def remove_scenario(scenario_id: int):
    """Elimina un escenario por su ID."""
    init_user_session()
    st.session_state.user_scenarios = [
        s for s in st.session_state.user_scenarios 
        if s["id"] != scenario_id
    ]


def clear_scenarios():
    """Limpia todos los escenarios del comparador."""
    st.session_state.user_scenarios = []


def get_scenario_count() -> int:
    """Retorna el número de escenarios activos."""
    init_user_session()
    return len(st.session_state.user_scenarios)


def show_autoload_widget():
    """Muestra widget para cargar datos guardados."""
    with st.expander("📤 ¿Tienes un respaldo guardado?", expanded=False):
        st.info("💡 Si descargaste un respaldo anteriormente, súbelo aquí para recuperar tus simulaciones.")
        
        uploaded = st.file_uploader(
            "Selecciona tu archivo JSON",
            type=["json"],
            key="autoload_file"
        )
        
        if uploaded:
            try:
                json_content = uploaded.read().decode("utf-8")
                success, message = import_simulations_json(json_content)
                if success:
                    st.success(message)
                    st.balloons()
                    st.rerun()
                else:
                    st.error(message)
            except Exception as e:
                st.error(f"❌ Error: {e}")


def show_history_tab():
    """Tab de histórico con expanders."""
    init_user_session()
    
    # Header con diseño mejorado - obtener tema del session_state
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
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center;">
        <h1 style="color: #FFFFFF !important; margin: 0; font-size: 2.5rem; font-weight: bold; -webkit-text-fill-color: #FFFFFF !important;">📜 Mi Histórico</h1>
        <p style="color: #FFFFFF !important; margin-top: 0.5rem; font-size: 1.1rem; opacity: 0.9; -webkit-text-fill-color: #FFFFFF !important;">
            Gestiona tus simulaciones guardadas
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    sim_count = get_simulation_count()
    
    # Info sobre persistencia
    st.info("""
    ⚠️ **Importante**: Los datos se mantienen mientras la pestaña esté abierta.  
    📥 **Descarga tu respaldo** antes de cerrar para no perder tus simulaciones.  
    📤 **Carga tu respaldo** cuando vuelvas para recuperar tus datos.
    """)
    
    # Controles de gestión
    st.markdown("### 🛠️ Gestión de Datos")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if sim_count > 0:
            json_data = export_simulations_json()
            filename = f"historial_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            st.download_button(
                label=f"📥 Descargar Respaldo ({sim_count})",
                data=json_data,
                file_name=filename,
                mime="application/json",
                width='stretch',
                type="primary"
            )
        else:
            st.button("📥 Descargar (0)", disabled=True, width='stretch')
    
    with col2:
        uploaded = st.file_uploader(
            "📤 Cargar respaldo",
            type=["json"],
            help="Sube tu archivo JSON guardado",
            key="history_upload",
            label_visibility="collapsed"
        )
        if uploaded:
            try:
                json_content = uploaded.read().decode("utf-8")
                success, message = import_simulations_json(json_content)
                if success:
                    st.success(message, icon="✅")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(message)
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    with col3:
        if sim_count > 0:
            if st.button("🗑️ Limpiar Todo", width='stretch', type="secondary"):
                clear_simulations()
                clear_scenarios()
                st.success("✅ Histórico limpiado")
                st.rerun()
        else:
            st.button("🗑️ Limpiar", disabled=True, width='stretch')
    
    st.markdown("---")
    
    sims = get_simulations(limit=100)
    
    if not sims:
        # Usar el gradiente del tema actual
        theme = st.session_state.get("current_theme", "Claro (default)")
        if "Verde" in theme:
            gradient = "linear-gradient(135deg, #059669 0%, #065F46 100%)"
        elif "Azul" in theme:
            gradient = "linear-gradient(135deg, #2563EB 0%, #1E3A8A 100%)"
        elif "Minimal" in theme:
            gradient = "linear-gradient(135deg, #525252 0%, #262626 100%)"
        else:
            gradient = "linear-gradient(135deg, #DC2626 0%, #7F1D1D 100%)"
        
        st.markdown(f"""
        <style>
            .gradient-header-white h1, .gradient-header-white h2, .gradient-header-white p {{
                color: #FFFFFF !important;
                -webkit-text-fill-color: #FFFFFF !important;
            }}
        </style>
        <div class="gradient-header-white" style="text-align: center; padding: 3rem; background: {gradient}; 
                    border-radius: 15px; margin-bottom: 2rem;">
            <h2 style="color: #FFFFFF !important; margin: 0; font-weight: bold; -webkit-text-fill-color: #FFFFFF !important;">📊 Sin simulaciones aún</h2>
            <p style="font-size: 1.1rem; color: #FFFFFF !important; margin-top: 0.5rem; opacity: 0.9; -webkit-text-fill-color: #FFFFFF !important;">Haz tu primera simulación en Acciones o Bonos</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Métricas
    total_acciones = len([s for s in sims if s["type"] == "Acciones"])
    total_bonos = len([s for s in sims if s["type"] == "Bonos"])
    valor_total_acciones = sum([s["results"].get("fv_total", 0) for s in sims if s["type"] == "Acciones"])
    valor_total_bonos = sum([s["results"].get("bond_pv", 0) for s in sims if s["type"] == "Bonos"])
    valor_total = valor_total_acciones + valor_total_bonos
    
    st.markdown("### 📈 Resumen General")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", len(sims))
    c2.metric("💰 Acciones", total_acciones)
    c3.metric("📈 Bonos", total_bonos)
    c4.metric("Valor", f"${valor_total:,.0f}")
    
    st.markdown("---")
    
    # Filtros
    cf1, cf2 = st.columns(2)
    with cf1:
        filter_type = st.selectbox("🔍 Filtrar", ["Todos", "Acciones", "Bonos"], key="filter")
    with cf2:
        sort_order = st.selectbox("📅 Ordenar", ["Más recientes", "Más antiguas"], key="sort")
    
    filtered = sims
    if filter_type != "Todos":
        filtered = [s for s in sims if s["type"].lower() == filter_type.lower()]
    if sort_order == "Más antiguas":
        filtered = filtered[::-1]
    
    st.markdown(f"**Mostrando {len(filtered)} de {len(sims)} simulaciones**")
    st.markdown("")
    
    # Expanders
    for sim in filtered:
        icon = "💰" if sim["type"] == "Acciones" else "📈"
        fecha = sim["timestamp"][:16].replace("T", " ")
        params = sim["params"]
        results = sim["results"]
        
        if sim["type"] == "Acciones":
            inicial = params.get("inicial", 0)
            valor = results.get("fv_total", 0)
            ganancia = results.get("ganancia_neta_retiro", 0)
            nombre = params.get("nombre", "Sin nombre")
            
            title = f"{icon} **Acciones #{sim['id']}** - {nombre} • {fecha} • ${valor:,.0f}"
            
            with st.expander(title, expanded=False):
                cm1, cm2, cm3 = st.columns(3)
                cm1.metric("💵 Inversión", f"${inicial:,.2f}")
                cm2.metric("📈 Valor Futuro", f"${valor:,.2f}")
                delta = f"+{(ganancia/inicial*100):.1f}%" if inicial > 0 else None
                cm3.metric("💰 Ganancia", f"${ganancia:,.2f}", delta=delta)
                
                st.markdown("---")
                
                cd1, cd2 = st.columns(2)
                with cd1:
                    st.markdown("#### 📋 Datos de inversión")
                    st.markdown(f"**👤 Nombre:** {params.get('nombre', 'N/A')}")
                    st.markdown(f"**📧 Correo:** {params.get('correo', 'N/A')}")
                    st.markdown(f"**🎂 Edad:** {params.get('edad', 'N/A')} años")
                    st.markdown(f"**💵 Inicial:** ${inicial:,.2f}")
                    st.markdown(f"**💸 Anualidad:** ${params.get('anualidad', 0):,.2f}")
                    st.markdown(f"**📊 TEA:** {params.get('tea_pct', 'N/A')}%")
                    st.markdown(f"**⏱️ Plazo:** {params.get('years', 'N/A')} años")
                    st.markdown(f"**🔄 Modalidad:** {params.get('modalidad', 'N/A')}")
                    st.markdown(f"**🏦 Bolsa:** {params.get('bolsa', 'N/A')}")
                
                with cd2:
                    st.markdown("#### 📊 Resultados")
                    st.markdown(f"**📈 Valor futuro:** ${valor:,.2f}")
                    st.markdown(f"**💰 Ganancia neta:** ${ganancia:,.2f}")
                    st.markdown(f"**💵 Dividendo anual:** ${results.get('dividendo_anual_neto', 0):,.2f}")
                    st.markdown(f"**📈 Total dividendos:** ${results.get('total_dividendos_periodo', 0):,.2f}")
                    if inicial > 0:
                        roi = (ganancia / inicial) * 100
                        st.markdown(f"**📊 ROI:** {roi:.2f}%")
                
                st.markdown("---")
                st.markdown("#### 🔄 Acciones")
                
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    if st.button("📊 Cargar esta simulación", key=f"load_acc_{sim['id']}", use_container_width=True, type="primary"):
                        # Cargar todos los datos al session_state para que aparezcan en resultados
                        st.session_state.update({
                            "initial": params.get("inicial", 0),
                            "annuity": params.get("anualidad", 0),
                            "years": params.get("years", 0),
                            "tea_pct": params.get("tea_pct", 0),
                            "modality": params.get("modalidad", "Mensual"),
                            "bolsa": params.get("bolsa", "BOLSA LOCAL (5%)"),
                            "nombre": params.get("nombre", ""),
                            "correo": params.get("correo", ""),
                            "edad": params.get("edad", 30),
                            "dividend_pct": params.get("dividend_pct"),
                            "fv_total": results.get("fv_total", 0),
                            "fv_init": results.get("fv_init", 0),
                            "fv_ann": results.get("fv_ann", 0),
                            "tax_rate": results.get("tax_rate", 0.05),
                            "total_invested": results.get("total_invested", 0),
                            "gain_before_tax": results.get("gain_before_tax", 0),
                            "tax_on_withdrawal": results.get("tax_on_withdrawal", 0),
                            "net_gain_withdrawal": ganancia,
                            "div_pct": results.get("div_pct", 0),
                            "annual_dividend": results.get("annual_dividend", 0),
                            "monthly_dividend": results.get("monthly_dividend", 0),
                            "net_monthly_dividend": results.get("dividendo_mensual_neto", 0),
                            "net_annual_dividend": results.get("dividendo_anual_neto", 0),
                            "total_net_dividends_over_period": results.get("total_dividendos_periodo", 0),
                            "r_period": results.get("r_period", 0),
                            "per_year": results.get("per_year", 12),
                            "n_periods": results.get("n_periods", 0),
                            "loaded_from_history": True
                        })
                        st.success(f"✅ Simulación #{sim['id']} cargada")
                        st.info("👉 Ve a la pestaña **Acciones** para ver los resultados y comparar con el mercado")
                        st.balloons()
                
                with col_a2:
                    if st.button("🗑️ Eliminar", key=f"del_acc_{sim['id']}", use_container_width=True):
                        st.session_state.user_simulations = [s for s in st.session_state.user_simulations if s["id"] != sim["id"]]
                        st.success("✅ Eliminada")
                        st.rerun()
                        
        else:  # Bonos
            valor_nominal = params.get("valor_nominal", 0)
            valor = results.get("bond_pv", 0)
            cupon = results.get("cupon_periodico", 0)
            nombre = params.get("nombre", "Sin nombre")
            
            title = f"{icon} **Bonos #{sim['id']}** - {nombre} • {fecha} • ${valor:,.0f}"
            
            with st.expander(title, expanded=False):
                cm1, cm2, cm3 = st.columns(3)
                cm1.metric("💵 Valor Nominal", f"${valor_nominal:,.2f}")
                cm2.metric("📊 Precio Justo", f"${valor:,.2f}")
                diferencia = valor - valor_nominal
                delta = f"{(diferencia/valor_nominal*100):.1f}%" if valor_nominal > 0 else None
                cm3.metric("💰 Diferencia", f"${diferencia:,.2f}", delta=delta)
                
                st.markdown("---")
                
                cd1, cd2 = st.columns(2)
                with cd1:
                    st.markdown("#### 📋 Datos del bono")
                    st.markdown(f"**👤 Nombre:** {params.get('nombre', 'N/A')}")
                    st.markdown(f"**📧 Correo:** {params.get('correo', 'N/A')}")
                    st.markdown(f"**🎂 Edad:** {params.get('edad', 'N/A')} años")
                    st.markdown(f"**💵 Valor nominal:** ${valor_nominal:,.2f}")
                    st.markdown(f"**📊 Tasa cupón:** {params.get('tasa_cupon_anual', 'N/A')}%")
                    st.markdown(f"**📈 TEA:** {params.get('tea_yield', 'N/A')}%")
                    st.markdown(f"**🔢 Períodos:** {params.get('periodos', 'N/A')}")
                    st.markdown(f"**⏱️ Tipo:** {params.get('periodo_tipo', 'N/A')}")
                
                with cd2:
                    st.markdown("#### 📊 Resultados")
                    st.markdown(f"**📊 Precio justo:** ${valor:,.2f}")
                    st.markdown(f"**💵 Cupón periódico:** ${cupon:,.2f}")
                    st.markdown(f"**🔢 Total períodos:** {results.get('periodos_totales', 0)}")
                    
                    if valor_nominal > 0:
                        if valor < valor_nominal:
                            st.success(f"✅ **Conviene** (descuento ${abs(diferencia):,.2f})")
                        elif valor > valor_nominal:
                            st.warning(f"⚠️ **Sobrevalorado** (premium ${diferencia:,.2f})")
                        else:
                            st.info("ℹ️ **A la par**")
                
                st.markdown("---")
                st.markdown("#### 🔄 Acciones")
                
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.button("📊 Cargar este bono", key=f"load_bond_{sim['id']}", use_container_width=True, type="primary"):
                        # Cargar todos los datos del bono al session_state
                        st.session_state.update({
                            "bond_face_value": valor_nominal,
                            "bond_coupon_rate": params.get("tasa_cupon_anual", 0),
                            "bond_tea_yield": params.get("tea_yield", 0),
                            "bond_period": params.get("periodo_tipo", "Anual"),
                            "bond_n_periods": params.get("periodos", 0),
                            "bond_pv": valor,
                            "bond_coupon_payment": cupon,
                            "bond_nombre": params.get("nombre", ""),
                            "bond_correo": params.get("correo", ""),
                            "bond_edad": params.get("edad", 30),
                            "loaded_bond_from_history": True
                        })
                        st.success(f"✅ Bono #{sim['id']} cargado")
                        st.info("👉 Ve a la pestaña **Bonos** para ver los resultados completos")
                        st.balloons()
                
                with col_b2:
                    if st.button("🗑️ Eliminar", key=f"del_bond_{sim['id']}", use_container_width=True):
                        st.session_state.user_simulations = [s for s in st.session_state.user_simulations if s["id"] != sim["id"]]
                        st.success("✅ Eliminado")
                        st.rerun()
