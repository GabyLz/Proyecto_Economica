import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO
from modules.finances_core import (
    evaluate_project,
    gradient_arithmetic,
    gradient_geometric,
    compare_projects
)

# -------------------------
# Configuración de tema y estilos
# -------------------------
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'danger': '#d62728',
    'info': '#17becf',
    'warning': '#ffbb00',
    'purple': '#9467bd',
    'gray': '#7f7f7f'
}

def get_base_layout():
    """Retorna configuración base para gráficos"""
    return {
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'font': {'family': 'Inter, sans-serif', 'size': 12, 'color': '#e0e0e0'},
        'xaxis': {'gridcolor': 'rgba(128,128,128,0.2)', 'showline': True, 'linecolor': 'rgba(128,128,128,0.3)'},
        'yaxis': {'gridcolor': 'rgba(128,128,128,0.2)', 'showline': True, 'linecolor': 'rgba(128,128,128,0.3)'},
        'hovermode': 'x unified'
    }

# -------------------------
# Helpers UI
# -------------------------
def download_df_as_csv(df: pd.DataFrame, filename: str = "resultados.csv"):
    buf = BytesIO()
    df.to_csv(buf, index=False, float_format="%.6f")
    buf.seek(0)
    st.download_button("📥 Descargar CSV", buf, file_name=filename, mime="text/csv")


def create_cashflow_chart(cashflows):
    """Crea un gráfico de flujo de caja mejorado con colores condicionales"""
    periods = list(range(len(cashflows)))
    colors = [COLORS['danger'] if cf < 0 else COLORS['success'] for cf in cashflows]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=periods,
        y=cashflows,
        marker=dict(
            color=colors,
            line=dict(color='rgba(255,255,255,0.3)', width=1.5)
        ),
        text=[f"${cf:,.0f}" for cf in cashflows],
        textposition='outside',
        hovertemplate='<b>Período %{x}</b><br>Flujo: $%{y:,.2f}<extra></extra>'
    ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.3)", line_width=1)
    
    fig.update_layout(
        **get_base_layout(),
        title={
            'text': "💰 Flujo de Caja por Período",
            'font': {'size': 16, 'color': '#ffffff'}
        },
        xaxis_title="Período",
        yaxis_title="Monto ($)",
        height=400,
        showlegend=False
    )
    
    return fig


def create_npv_profile_chart(npv_profile, tir_value=None):
    """Crea un gráfico del perfil VAN vs TMAR mejorado"""
    prof_df = pd.DataFrame(npv_profile, columns=["tmar", "van"])
    
    fig = go.Figure()
    
    # Línea principal
    fig.add_trace(go.Scatter(
        x=prof_df["tmar"] * 100,
        y=prof_df["van"],
        mode='lines+markers',
        name='VAN',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=6, color=COLORS['primary']),
        fill='tozeroy',
        fillcolor='rgba(31, 119, 180, 0.1)',
        hovertemplate='<b>TMAR: %{x:.2f}%</b><br>VAN: $%{y:,.2f}<extra></extra>'
    ))
    
    # Línea en cero
    fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.4)", line_width=2)
    
    # Marcar TIR si existe
    if tir_value is not None and not np.isnan(tir_value):
        fig.add_vline(
            x=tir_value * 100,
            line_dash="dot",
            line_color=COLORS['warning'],
            line_width=2,
            annotation_text=f"TIR: {tir_value*100:.2f}%",
            annotation_position="top"
        )
    
    fig.update_layout(
        **get_base_layout(),
        title={
            'text': "📊 Perfil VAN vs Tasa de Descuento",
            'font': {'size': 16, 'color': '#ffffff'}
        },
        xaxis_title="TMAR (%)",
        yaxis_title="VAN ($)",
        height=450,
        showlegend=False
    )
    
    return fig


def create_montecarlo_chart(mc_samples):
    """Crea un histograma mejorado para Monte Carlo"""
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=mc_samples,
        nbinsx=50,
        marker=dict(
            color=COLORS['info'],
            line=dict(color='white', width=1)
        ),
        hovertemplate='<b>Rango VAN:</b> %{x:,.0f}<br><b>Frecuencia:</b> %{y}<extra></extra>'
    ))
    
    # Añadir línea de media
    mean_val = np.mean(mc_samples)
    fig.add_vline(
        x=mean_val,
        line_dash="dash",
        line_color=COLORS['warning'],
        line_width=2,
        annotation_text=f"Media: ${mean_val:,.0f}",
        annotation_position="top right"
    )
    
    fig.update_layout(
        **get_base_layout(),
        title={
            'text': "🎲 Distribución Monte Carlo del VAN",
            'font': {'size': 16, 'color': '#ffffff'}
        },
        xaxis_title="VAN ($)",
        yaxis_title="Frecuencia",
        height=400,
        showlegend=False
    )
    
    return fig


def create_ranking_chart(df_rank):
    """Crea un gráfico de ranking multicriterio mejorado"""
    colors_gradient = [COLORS['success'] if i == 0 else COLORS['primary'] if i < 3 else COLORS['gray'] 
                       for i in range(len(df_rank))]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_rank["name"],
        y=df_rank["score"],
        marker=dict(
            color=colors_gradient,
            line=dict(color='rgba(255,255,255,0.3)', width=1.5)
        ),
        text=[f"{s:.3f}" for s in df_rank["score"]],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Score: %{y:.4f}<extra></extra>'
    ))
    
    fig.update_layout(
        **get_base_layout(),
        title={
            'text': "🏆 Ranking Multicriterio de Proyectos",
            'font': {'size': 16, 'color': '#ffffff'}
        },
        xaxis_title="Proyecto",
        yaxis_title="Puntaje Normalizado",
        height=400,
        showlegend=False
    )
    
    return fig


# ----------------------------------------------------------
# MAIN UI
# ----------------------------------------------------------
def show_project_evaluator():

    # --------------------------
    # 🔧 Inicializar session_state
    # --------------------------
    if "projects_list" not in st.session_state:
        st.session_state.projects_list = []
    if "selected_project_name" not in st.session_state:
        st.session_state.selected_project_name = None
    if "edit_project" not in st.session_state:
        st.session_state.edit_project = None

    # Header mejorado
    st.markdown("---")
    
    # --------------------------
    # SECCIÓN 1: Crear proyecto
    # --------------------------
    with st.expander("➕ **CREAR NUEVO PROYECTO**", expanded=len(st.session_state.projects_list) == 0):
        with st.form("project_form", clear_on_submit=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                name = st.text_input(
                    "📝 Nombre del proyecto",
                    value=f"Proyecto {len(st.session_state.projects_list)+1}",
                    help="Identifica tu proyecto con un nombre único"
                )
            
            with col2:
                tmar = st.number_input(
                    "📈 TMAR (%)",
                    value=12.0,
                    min_value=0.0,
                    max_value=100.0,
                    step=0.5,
                    help="Tasa Mínima Atractiva de Retorno"
                ) / 100
            
            col3, col4 = st.columns(2)
            
            with col3:
                n = st.number_input(
                    "📅 Horizonte (años)",
                    value=5,
                    min_value=1,
                    max_value=50,
                    step=1,
                    help="Duración del proyecto en años"
                )
            
            with col4:
                flow_type = st.selectbox(
                    "💵 Tipo de flujo",
                    ["Constante", "Gradiente aritmético", "Gradiente geométrico", "Manual"],
                    help="Selecciona cómo quieres definir los flujos de caja"
                )
            
            st.markdown("---")
            
            # Inversión inicial
            c0 = st.number_input(
                "💰 Inversión inicial (C0)",
                value=-10000.0,
                help="Monto de inversión inicial (negativo)"
            )
            
            # Configuración según tipo de flujo
            if flow_type == "Constante":
                f = st.number_input("💵 Flujo anual constante", value=3000.0)
                cashflows = [c0] + [f] * int(n)
                
            elif flow_type == "Gradiente aritmético":
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    f0 = st.number_input("💵 Flujo base (F0)", value=2000.0)
                with col_a2:
                    g = st.number_input("📊 Gradiente (G)", value=300.0, help="Incremento anual constante")
                cashflows = [c0] + gradient_arithmetic(f0, g, int(n))
                
            elif flow_type == "Gradiente geométrico":
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    f0 = st.number_input("💵 Flujo inicial (F0)", value=2000.0)
                with col_g2:
                    g_pct = st.number_input("📈 Crecimiento (%)", value=5.0, step=0.5) / 100
                cashflows = [c0] + gradient_geometric(f0, g_pct, int(n))
                
            else:  # Manual
                st.info("📝 Ingresa los flujos manualmente para cada año:")
                cols_manual = st.columns(min(5, int(n)))
                manual = [c0]
                for i in range(1, int(n) + 1):
                    with cols_manual[(i-1) % 5]:
                        manual.append(st.number_input(f"Año {i}", value=0.0, key=f"m_{i}"))
                cashflows = manual
            
            # Opciones Monte Carlo
            st.markdown("---")
            st.markdown("**🎲 Análisis de Riesgo (Monte Carlo)**")
            
            col_mc1, col_mc2, col_mc3 = st.columns(3)
            with col_mc1:
                mc_sim = st.checkbox("Activar simulación Monte Carlo", value=False)
            
            with col_mc2:
                mc_n = st.number_input(
                    "Nº simulaciones",
                    value=1000,
                    min_value=100,
                    max_value=20000,
                    step=100
                ) if mc_sim else 0
            
            with col_mc3:
                mc_sigma = st.slider(
                    "Volatilidad (σ)",
                    0.01, 0.5, 0.15,
                    help="Desviación estándar relativa de los flujos"
                ) if mc_sim else 0.15
            
            submitted = st.form_submit_button("✅ AGREGAR PROYECTO", use_container_width=True, type="primary")
        
        if submitted:
            spec = {
                "name": name or f"Proyecto_{len(st.session_state.projects_list)+1}",
                "cashflows": cashflows,
                "tmar": tmar,
                "mc": mc_sim,
                "mc_n": int(mc_n),
                "mc_sigma": float(mc_sigma)
            }
            st.session_state.projects_list.append(spec)
            st.success(f"✅ Proyecto '{spec['name']}' agregado exitosamente")
            st.rerun()

    st.markdown("---")
    
    # --------------------------
    # SECCIÓN 2: Lista de proyectos
    # --------------------------
    st.subheader("📂 Proyectos Registrados")
    
    if not st.session_state.projects_list:
        st.info("ℹ️ No hay proyectos registrados. Crea uno en la sección anterior.")
        st.stop()
    
    # Controles superiores
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 1, 1])
    
    # Obtener nombres de proyectos
    nombres = [p["name"] for p in st.session_state.projects_list]
    
    # Inicializar con el primer proyecto si no hay selección
    if st.session_state.selected_project_name is None or st.session_state.selected_project_name not in nombres:
        st.session_state.selected_project_name = nombres[0] if nombres else None
    
    with col_ctrl1:
        # Selectbox basado en NOMBRE no en índice
        selected_name = st.selectbox(
            "🎯 Selecciona un proyecto para analizar:",
            options=nombres,
            index=nombres.index(st.session_state.selected_project_name) if st.session_state.selected_project_name in nombres else 0,
            key="project_selector_key"
        )
    
    # ACTUALIZAR el nombre seleccionado
    st.session_state.selected_project_name = selected_name
    
    # OBTENER el índice del proyecto seleccionado por nombre
    sel_idx = None
    for idx, p in enumerate(st.session_state.projects_list):
        if p["name"] == selected_name:
            sel_idx = idx
            break
        
    st.session_state.selected_project = sel_idx
    
    with col_ctrl2:
        if st.button("🗑️ Limpiar Todo", use_container_width=True):
            st.session_state.projects_list = []
            st.session_state.selected_project = None
            st.rerun()
    
    with col_ctrl3:
        st.metric("Total", len(st.session_state.projects_list), label_visibility="visible")
    
    # Lista expandible de proyectos
    st.markdown("##### 📋 Lista completa:")
    for idx, p in enumerate(st.session_state.projects_list):
        is_selected = p["name"] == st.session_state.selected_project_name
        with st.expander(f"{'🔵' if is_selected else '⚪'} {idx+1}. {p['name']}", expanded=False):
            col_info1, col_info2, col_info3 = st.columns(3)
            col_info1.metric("TMAR", f"{p['tmar']*100:.2f}%")
            col_info2.metric("Períodos", len(p['cashflows'])-1)
            col_info3.metric("Monte Carlo", "Sí ✓" if p['mc'] else "No")
            
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            if col_btn1.button("👁 Ver", key=f"ver_{idx}", use_container_width=True):
                st.session_state.selected_project_name = p["name"]
                st.rerun()
            if col_btn2.button("✏️ Editar", key=f"edit_{idx}", use_container_width=True):
                st.session_state.edit_project = idx
                st.rerun()
            if col_btn3.button("🗑 Eliminar", key=f"del_{idx}", use_container_width=True):
                deleted_name = p["name"]
                st.session_state.projects_list.pop(idx)
                # Si eliminamos el proyecto seleccionado, seleccionar el primero
                if st.session_state.selected_project_name == deleted_name:
                    st.session_state.selected_project_name = st.session_state.projects_list[0]["name"] if st.session_state.projects_list else None
                st.success("✅ Proyecto eliminado")
                st.rerun()
    
    # Obtener el índice del proyecto seleccionado desde el selectbox
    # Validar índice antes de continuar
    if  sel_idx is None:
        sel_idx = 0

    if sel_idx < 0 or sel_idx >= len(st.session_state.projects_list):
        sel_idx = 0

    st.session_state.selected_project = sel_idx
    
    # --------------------------
    # Edición de proyecto
    # --------------------------
    if st.session_state.edit_project is not None:
        idx = st.session_state.edit_project
        proj = st.session_state.projects_list[idx]
        
        st.markdown("---")
        st.subheader(f"✏️ Editar: {proj['name']}")
        
        with st.form("edit_form"):
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                new_name = st.text_input("Nombre", proj["name"])
            with col_e2:
                new_tmar = st.number_input("TMAR (%)", value=proj["tmar"]*100, step=0.5) / 100
            
            col_e3, col_e4, col_e5 = st.columns(3)
            with col_e3:
                mc_sim = st.checkbox("Monte Carlo", value=proj["mc"])
            with col_e4:
                mc_n = st.number_input("Simulaciones", value=proj["mc_n"], step=100) if mc_sim else proj["mc_n"]
            with col_e5:
                mc_sigma = st.slider("σ", 0.01, 0.5, proj["mc_sigma"]) if mc_sim else proj["mc_sigma"]
            
            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.form_submit_button("💾 Guardar", use_container_width=True, type="primary"):
                    proj.update({
                        "name": new_name,
                        "tmar": new_tmar,
                        "mc": mc_sim,
                        "mc_n": mc_n,
                        "mc_sigma": mc_sigma
                    })
                    st.session_state.edit_project = None
                    st.success("✅ Proyecto actualizado")
                    st.rerun()
            
            with col_cancel:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    st.session_state.edit_project = None
                    st.rerun()
    
    st.markdown("---")
    
    # --------------------------
    # SECCIÓN 3: Evaluación del proyecto seleccionado
    # --------------------------
    
    # CRÍTICO: Usar sel_idx para obtener el proyecto correcto
    project = st.session_state.projects_list[sel_idx]
    
    with st.spinner('⚙️ Evaluando proyecto...'):
        metrics = evaluate_project(
            project["cashflows"],
            project["tmar"],
            montecarlo=project["mc"],
            mc_nsim=project["mc_n"],
            mc_sigma=project["mc_sigma"]
        )
    
    st.markdown(f"## 📊 Análisis: **{project['name']}**")
    
    # Métricas principales con formato mejorado
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    van_val = metrics['van']
    tir_val = metrics['tir']
    bc_val = metrics['b_c']
    
    with col_m1:
        st.metric(
            "💰 VAN",
            f"${van_val:,.2f}",
            delta="Viable" if van_val > 0 else "No viable",
            delta_color="normal" if van_val > 0 else "inverse"
        )
    
    with col_m2:
        if tir_val is not None and not np.isnan(tir_val):
            tir_display = f"{(tir_val*100):.2f}%"
            tir_delta = "✓ > TMAR" if tir_val > project['tmar'] else "✗ < TMAR"
            tir_color = "normal" if tir_val > project['tmar'] else "inverse"
        else:
            tir_display = "N/A"
            tir_delta = None
            tir_color = "off"
        st.metric("📉 TIR", tir_display, delta=tir_delta, delta_color=tir_color)
    
    with col_m3:
        if bc_val is not None:
            bc_display = f"{bc_val:.3f}"
            bc_delta = "Rentable" if bc_val > 1 else "No rentable"
            bc_color = "normal" if bc_val > 1 else "inverse"
        else:
            bc_display = "N/A"
            bc_delta = None
            bc_color = "off"
        st.metric("📘 B/C", bc_display, delta=bc_delta, delta_color=bc_color)
    
    with col_m4:
        st.metric("📅 Períodos", f"{len(project['cashflows'])-1} años")
    
    st.markdown("---")
    
    # Gráficos principales
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Flujo de Caja", "📈 Perfil VAN", "🎲 Monte Carlo", "📋 Datos"])
    
    with tab1:
        fig_cf = create_cashflow_chart(project["cashflows"])
        st.plotly_chart(fig_cf, use_container_width=True)
        
        # Resumen de flujos
        col_sum1, col_sum2, col_sum3 = st.columns(3)
        total_inflows = sum([f for f in project["cashflows"] if f > 0])
        total_outflows = sum([f for f in project["cashflows"] if f < 0])
        col_sum1.metric("💰 Total Ingresos", f"${total_inflows:,.2f}")
        col_sum2.metric("💸 Total Egresos", f"${total_outflows:,.2f}")
        col_sum3.metric("📊 Flujo Neto", f"${total_inflows + total_outflows:,.2f}")
        
        # Tabla de flujos
        with st.expander("📋 Ver tabla detallada de flujos"):
            df_cf = pd.DataFrame({
                "Período": range(len(project["cashflows"])),
                "Flujo ($)": project["cashflows"],
                "Tipo": ["Inversión" if i == 0 else "Ingreso" if f > 0 else "Egreso" for i, f in enumerate(project["cashflows"])]
            })
            st.dataframe(df_cf, use_container_width=True, hide_index=True)
    
    with tab2:
        fig_prof = create_npv_profile_chart(metrics["npv_profile"], tir_val)
        st.plotly_chart(fig_prof, use_container_width=True)
        
        st.info(f"💡 **Interpretación:** El VAN es cero cuando la tasa de descuento = TIR ({tir_val*100:.2f}%)" if tir_val else "⚠️ TIR no disponible")
    
    with tab3:
        if "montecarlo" in metrics:
            mc = metrics["montecarlo"]
            
            fig_mc = create_montecarlo_chart(mc["samples"])
            st.plotly_chart(fig_mc, use_container_width=True)
            
            # Estadísticas MC
            col_mc1, col_mc2, col_mc3, col_mc4 = st.columns(4)
            col_mc1.metric("📊 Media", f"${mc['mean']:,.2f}")
            col_mc2.metric("📍 P50 (Mediana)", f"${mc['p50']:,.2f}")
            col_mc3.metric("⚠️ P5 (Riesgo)", f"${mc['p5']:,.2f}")
            col_mc4.metric("🎯 P95", f"${mc.get('p95', np.percentile(mc['samples'], 95)):,.2f}")
            
            # Probabilidad de VAN positivo
            prob_positive = np.sum(np.array(mc["samples"]) > 0) / len(mc["samples"]) * 100
            st.progress(prob_positive / 100)
            st.markdown(f"**Probabilidad de VAN > 0:** {prob_positive:.1f}%")
            
            # Interpretación
            if prob_positive >= 75:
                st.success(f"✅ Alta probabilidad de éxito ({prob_positive:.1f}%). Proyecto robusto.")
            elif prob_positive >= 50:
                st.warning(f"⚠️ Probabilidad moderada ({prob_positive:.1f}%). Requiere análisis detallado.")
            else:
                st.error(f"❌ Baja probabilidad de éxito ({prob_positive:.1f}%). Proyecto riesgoso.")
        else:
            st.info("ℹ️ Monte Carlo no activado para este proyecto. Edítalo para habilitarlo.")
    
    with tab4:
        st.markdown("#### 📝 Información del Proyecto")
        info_data = {
            "Nombre": project["name"],
            "TMAR": f"{project['tmar']*100:.2f}%",
            "Horizonte": f"{len(project['cashflows'])-1} años",
            "Inversión Inicial": f"${project['cashflows'][0]:,.2f}",
            "VAN": f"${metrics['van']:,.2f}",
            "TIR": f"{metrics['tir']*100:.2f}%" if metrics['tir'] else "N/A",
            "B/C": f"{metrics['b_c']:.3f}" if metrics['b_c'] else "N/A",
            "Monte Carlo": "Activado ✓" if project['mc'] else "No activado",
        }
        
        for key, value in info_data.items():
            col1, col2 = st.columns([1, 2])
            col1.markdown(f"**{key}:**")
            col2.markdown(value)
        
        st.markdown("---")
        st.markdown("#### 📊 Flujos de Caja Completos")
        df_full = pd.DataFrame({
            "Período": range(len(project["cashflows"])),
            "Flujo ($)": [f"{f:,.2f}" for f in project["cashflows"]],
            "Acumulado ($)": [f"{sum(project['cashflows'][:i+1]):,.2f}" for i in range(len(project["cashflows"]))]
        })
        st.dataframe(df_full, use_container_width=True, hide_index=True)
    
    # --------------------------
    # Exportación
    # --------------------------
    st.markdown("---")
    st.subheader("💾 Exportar Resultados")
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        df_cashflows = pd.DataFrame({
            "period": range(len(project["cashflows"])),
            "cashflow": project["cashflows"]
        })
        st.download_button(
            "📥 Descargar Flujos (CSV)",
            df_cashflows.to_csv(index=False),
            file_name=f"{project['name']}_cashflows.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_exp2:
        df_summary = pd.DataFrame([{
            "Proyecto": project["name"],
            "VAN": metrics["van"],
            "TIR": metrics["tir"] if metrics["tir"] else "N/A",
            "B/C": metrics["b_c"] if metrics["b_c"] else "N/A",
            "TMAR": project["tmar"],
            "Períodos": len(project["cashflows"]) - 1
        }])
        st.download_button(
            "📥 Descargar Resumen (CSV)",
            df_summary.to_csv(index=False),
            file_name=f"{project['name']}_summary.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # --------------------------
    # SECCIÓN 4: Comparación multicriterio
    # --------------------------
    if len(st.session_state.projects_list) > 1:
        st.markdown("---")
        st.subheader("🏆 Comparación Multicriterio")
        st.caption("Compara todos los proyectos usando pesos personalizados")
        
        # Configuración de pesos
        col_w1, col_w2, col_w3, col_w4 = st.columns(4)
        
        with col_w1:
            w_van = st.slider("💰 Peso VAN", 0.0, 1.0, 0.5, 0.05)
        with col_w2:
            w_tir = st.slider("📉 Peso TIR", 0.0, 1.0, 0.3, 0.05)
        with col_w3:
            w_bc = st.slider("📘 Peso B/C", 0.0, 1.0, 0.2, 0.05)
        with col_w4:
            total_w = w_van + w_tir + w_bc
            st.metric("Total", f"{total_w:.2f}", delta="OK" if abs(total_w - 1.0) < 0.01 else "Ajustar")
        
        # Normalizar pesos
        total_w = max(total_w, 1e-6)
        weights = {
            "van": w_van / total_w,
            "tir": w_tir / total_w,
            "b_c": w_bc / total_w
        }
        
        # Calcular ranking
        proj_metrics = []
        for p in st.session_state.projects_list:
            m = evaluate_project(p["cashflows"], p["tmar"], montecarlo=False)
            proj_metrics.append({
                "name": p["name"],
                "metrics": {
                    "van": m["van"],
                    "tir": m["tir"] or 0.0,
                    "b_c": m["b_c"] or 0.0
                }
            })
        
        ranking = compare_projects(proj_metrics, weights=weights)
        df_rank = pd.DataFrame(ranking)
        
        # Mostrar ranking
        col_rank1, col_rank2 = st.columns([1, 2])
        
        with col_rank1:
            st.markdown("##### 📊 Tabla de Ranking")
            st.dataframe(
                df_rank.style.background_gradient(subset=['score'], cmap='RdYlGn'),
                use_container_width=True,
                hide_index=True
            )
        
        with col_rank2:
            st.markdown("##### 📈 Gráfico Comparativo")
            fig_rank = create_ranking_chart(df_rank)
            st.plotly_chart(fig_rank, use_container_width=True)
        
        # Exportar ranking
        st.download_button(
            "📥 Descargar Ranking Completo (CSV)",
            df_rank.to_csv(index=False),
            file_name="ranking_proyectos.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    else:
        st.info("ℹ️ Agrega más proyectos para habilitar la comparación multicriterio")