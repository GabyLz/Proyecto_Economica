"""
Módulo de chatbot financiero inteligente.
Asistente conversacional para asesoría financiera personalizada.
"""

import streamlit as st
from openai import OpenAI
from datetime import datetime
from typing import List, Dict


def init_chatbot_session():
    """Inicializa el estado del chatbot."""
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
        # Agregar mensaje de bienvenida automático
        welcome_message = """👋 **¡Bienvenido a tu Asistente Financiero IA!**

Soy tu consultor personal para inversiones en **Acciones** y **Bonos**. Puedo ayudarte a:

💡 **Recomendaciones para empezar:**
- ✅ Primero realiza una simulación en las pestañas de *Acciones* o *Bonos*
- ✅ Luego pregúntame sobre tus resultados, riesgos o estrategias
- ✅ Puedo comparar tu inversión con el mercado real (S&P 500)
- ✅ Pregunta sobre conceptos: TEA, dividendos, volatilidad, etc.

**Ejemplos de preguntas:**
- "¿Mi proyección es realista?"
- "¿Conviene retirar todo o solo dividendos?"
- "Explícame qué es el TEA"
- "Compara mi simulación con el S&P 500"

¡Adelante, pregúntame lo que necesites! 🚀
"""
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": welcome_message,
            "timestamp": datetime.now().isoformat()
        })
    
    if "chat_context" not in st.session_state:
        st.session_state.chat_context = {
            "user_simulations": [],
            "current_simulation": None,
            "user_profile": {}
        }


def add_message(role: str, content: str):
    """Agrega mensaje al historial."""
    st.session_state.chat_messages.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })


def get_context_summary() -> str:
    """Genera resumen del contexto del usuario."""
    ctx = st.session_state.chat_context
    summary_parts = []
    
    # Simulación actual
    if "fv_total" in st.session_state:
        summary_parts.append(f"""
**Simulación activa (Acciones)**:
- Inversión inicial: ${st.session_state.get('initial', 0):,.2f}
- Anualidad: ${st.session_state.get('annuity', 0):,.2f}
- TEA: {st.session_state.get('tea_pct', 0)}%
- Plazo: {st.session_state.get('years', 0)} años
- Valor futuro: ${st.session_state.get('fv_total', 0):,.2f}
- Ganancia neta: ${st.session_state.get('net_gain_withdrawal', 0):,.2f}
""")
    
    if "bond_pv" in st.session_state:
        summary_parts.append(f"""
**Bono activo**:
- Valor nominal: ${st.session_state.get('bond_face_value', 0):,.2f}
- Tasa cupón: {st.session_state.get('bond_coupon_rate', 0)}%
- TEA: {st.session_state.get('bond_tea_yield', 0)}%
- Precio justo: ${st.session_state.get('bond_pv', 0):,.2f}
""")
    
    # Histórico
    if "user_simulations" in st.session_state and st.session_state.user_simulations:
        total_sims = len(st.session_state.user_simulations)
        summary_parts.append(f"\n**Histórico**: {total_sims} simulaciones guardadas")
    
    return "\n".join(summary_parts) if summary_parts else "Sin datos de simulación activa"


def show_chatbot():
    """Muestra el chatbot en una interfaz elegante."""
    init_chatbot_session()
    
    # Header del chatbot - obtener tema
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
        .gradient-header-white h2, .gradient-header-white p {{
            color: #FFFFFF !important;
        }}
    </style>
    <div class="gradient-header-white" style="background: {gradient}; 
                padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem; text-align: center;">
        <h2 style="color: #FFFFFF !important; margin: 0; font-size: 2rem; font-weight: bold; -webkit-text-fill-color: #FFFFFF !important;">💬 Asistente Financiero IA</h2>
        <p style="color: #FFFFFF !important; margin-top: 0.5rem; opacity: 0.9; -webkit-text-fill-color: #FFFFFF !important;">
            Pregúntame cualquier cosa sobre tus inversiones
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sugerencias rápidas (colapsado por defecto)
    with st.expander("❓ Ejemplos de preguntas que puedes hacer", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📊 Sobre tu simulación:**
            - "¿Mi proyección es realista?"
            - "¿Cuál es el riesgo de esta inversión?"
            - "¿Conviene retirar todo o solo dividendos?"
            - "¿Cómo puedo mejorar mi rendimiento?"
            
            **📚 Educación financiera:**
            - "Explícame qué es el TEA"
            - "¿Qué diferencia hay entre CAGR y TEA?"
            - "¿Cómo funciona la volatilidad?"
            - "¿Qué es diversificación?"
            """)
        
        with col2:
            st.markdown("""
            **🔍 Análisis comparativo:**
            - "Compara mi simulación con el S&P 500"
            - "¿Qué acciones tienen rendimiento similar?"
            - "¿Mis expectativas son optimistas?"
            
            **💰 Estrategias:**
            - "¿Debería invertir más en bonos o acciones?"
            - "¿Cómo afectan los impuestos a mi ganancia?"
            - "¿Cuándo debo rebalancear mi portafolio?"
            """)
    
    # Contenedor de mensajes con scroll
    chat_container = st.container()
    
    with chat_container:
        # Mostrar historial
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(msg["content"])
    
    # Input del usuario
    user_input = st.chat_input("Escribe tu pregunta aquí...")
    
    if user_input:
        # Agregar mensaje del usuario
        add_message("user", user_input)
        
        # Mostrar mensaje del usuario inmediatamente
        with chat_container:
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_input)
        
        # Generar respuesta
        with chat_container:
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Pensando..."):
                    try:
                        # Construir contexto
                        context_summary = get_context_summary()
                        
                        # Historial de conversación para contexto
                        conversation_history = "\n".join([
                            f"{'Usuario' if m['role'] == 'user' else 'Asistente'}: {m['content']}"
                            for m in st.session_state.chat_messages[-10:]  # Últimos 10 mensajes
                        ])
                        
                        # Prompt para GPT
                        system_prompt = f"""
Eres un asistente financiero experto y amigable. Tu objetivo es ayudar al usuario con sus inversiones en acciones y bonos.

**Contexto del usuario:**
{context_summary}

**Conversación reciente:**
{conversation_history}

**Instrucciones:**
1. Responde de forma clara, profesional pero cercana
2. Usa el contexto de la simulación actual para respuestas personalizadas
3. Si preguntan sobre datos específicos, usa la información del contexto
4. Educa sobre conceptos financieros cuando sea relevante
5. Sé breve pero completo (máximo 250 palabras)
6. Usa emojis moderadamente para hacer la lectura más amena
7. Si no tienes datos suficientes, indícalo y sugiere qué calcular
8. **IMPORTANTE**: Para fórmulas matemáticas, usa el formato de Streamlit:
   - Para ecuaciones inline: $formula$
   - Para bloques de ecuaciones: $$formula$$
   - Ejemplo inline: $P = \\frac{{1000000}}{{(1 + 0.12)^5}}$
   - Ejemplo bloque: $$P = \\frac{{1000000}}{{(1 + 0.12)^5}}$$
   - NUNCA uses corchetes [ ] para fórmulas LaTeX
9. Puedes ayudar a el usuario a interpretar resultados financieros complejos de manera sencilla.
10. Tu nombre es Panchito, el asistente financiero IA de Inversor Inteligente.
**Pregunta del usuario:**
{user_input}
"""
                        
                        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                        
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": system_prompt}
                            ],
                            max_tokens=500,
                            temperature=0.7
                        )
                        
                        bot_response = response.choices[0].message.content
                        
                        # Mostrar respuesta
                        st.markdown(bot_response)
                        
                        # Guardar respuesta
                        add_message("assistant", bot_response)
                        
                    except Exception as e:
                        error_msg = f"⚠️ Error al procesar tu pregunta: {str(e)}"
                        st.error(error_msg)
                        add_message("assistant", error_msg)
    
    # Botón para limpiar chat
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🗑️ Limpiar conversación", width='stretch', type="secondary"):
            st.session_state.chat_messages = []
            st.rerun()
    
    # Contador de mensajes
    st.caption(f"💬 {len(st.session_state.chat_messages)} mensajes en esta conversación")


def show_chatbot_compact():
    """Versión compacta del chatbot para sidebar."""
    init_chatbot_session()
    
    st.markdown("### 💬 Chat Rápido")
    st.caption("Asistente financiero IA")
    
    # Últimos 3 mensajes
    recent_messages = st.session_state.chat_messages[-3:] if st.session_state.chat_messages else []
    
    for msg in recent_messages:
        if msg["role"] == "user":
            st.markdown(f"**👤 Tú:** {msg['content'][:50]}...")
        else:
            st.markdown(f"**🤖 IA:** {msg['content'][:50]}...")
    
    # Input compacto
    with st.form("chat_compact_form", clear_on_submit=True):
        user_input = st.text_input("Pregunta rápida:", key="chat_compact_input")
        submitted = st.form_submit_button("Enviar", width='stretch')
        
        if submitted and user_input:
            add_message("user", user_input)
            
            try:
                context_summary = get_context_summary()
                
                system_prompt = f"""
Eres un asistente financiero. Responde en máximo 2 líneas de forma concisa.

**IMPORTANTE**: Si usas fórmulas matemáticas, usa formato Streamlit: $formula$ para inline o $$formula$$ para bloques. NUNCA uses corchetes [ ].

Contexto:
{context_summary}

Pregunta: {user_input}
"""
                
                client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": system_prompt}],
                    max_tokens=150,
                    temperature=0.7
                )
                
                bot_response = response.choices[0].message.content
                add_message("assistant", bot_response)
                st.success("✅ Respuesta enviada")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    if st.button("💬 Ver chat completo", width='stretch', type="primary"):
        st.session_state.show_full_chat = True
        st.rerun()
