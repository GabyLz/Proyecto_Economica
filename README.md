# 📊 Simulador Real de Inversiones y Bonos

> **Una herramienta profesional de simulación financiera con IA integrada para análisis de inversiones en acciones y bonos**

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?logo=streamlit&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?logo=openai&logoColor=white)
![Licencia](https://img.shields.io/badge/Licencia-MIT-green)

## 🎯 Características Principales

### 💰 Simulador de Acciones
- **Cálculo de valor futuro** con inversión inicial y aportes periódicos
- **Modelado de dividendos** ajustables según estrategia
- **TEA personalizable** (Tasa Efectiva Anual)
- **Múltiples frecuencias** de aporte (Mensual, Trimestral, Semestral, Anual)
- **Comparación con mercado real** (Yahoo Finance)
- **Análisis de volatilidad** e indicadores técnicos

### 📈 Analizador de Bonos
- **Cálculo de valor presente** (PV) de bonos
- **Análisis de spreads** vs. bonos de mercado real
- **Comparables de mercado** (Tesoro USA, Corporativos, Emergentes)
- **Clasificación de riesgo** (Muy Conservador → Muy Optimista)
- **Múltiples períodos** de cupón (Mensual, Trimestral, Semestral, Anual)

### 🤖 Asistente Financiero con IA
- **Chat conversacional** con GPT-4o-mini
- **Análisis personalizado** de inversiones
- **Recomendaciones** basadas en contexto
- **Educación financiera** integrada
- **Historial conversacional** persistente

### 📜 Gestión de Datos
- **Histórico de simulaciones** guardadas
- **Exportación a JSON** para respaldo
- **Importación de escenarios** previos
- **Comparador de escenarios** lado a lado
- **Descarga de reportes PDF** profesionales

### 🎨 Interfaz Moderna
- **Temas personalizables** (Claro, Verde, Azul, Minimal)
- **Modo compacto** para pantallas pequeñas
- **Presets predefinidos** para inicio rápido
- **Gráficos interactivos** con Plotly
- **Reportes profesionales** con PDF descargable
- **Soporte integrado**: Código QR que conecta con WhatsApp de soporte técnico

### 💱 Conversor de Monedas (FX)
- **Tasas en tiempo real** (API gratuita - open.er-api.com, sin clave requerida)
- **Soporte para 45+ monedas** incluyendo todas las latinoamericanas: ARS, MXN, BRL, CLP, COP, PEN, UYU, VES
- **Panel dinámico de tasas** mostrando monedas relevantes vs. moneda de referencia
- **Indicadores visuales de fuente**: 🔴 Tasa en tiempo real (API), 🟡 Tasa en cache (última hora), 🟢 Tasa manual
- **Cache inteligente** con TTL de 1 hora y persistencia en JSON
- **Fallback manual** si la API no está disponible
- **Última conversión mostrada** con detalles completos
- **Reintentos automáticos** con backoff exponencial (3 intentos)
- **Auditoría completa** (timestamp, fuente, proveedor, tasa aplicada)

## 🚀 Inicio Rápido

### Requisitos Previos
- Python 3.9 o superior
- pip (gestor de paquetes de Python)
- Clave de API de OpenAI ([obtener aquí](https://platform.openai.com/api-keys))

### Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/GabyLz/Proyecto_Economica.git
cd Proyecto_Economica
```

2. **Crear entorno virtual** (recomendado)
```bash
python -m venv venv

# En Windows:
venv\Scripts\activate

# En macOS/Linux:
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar credenciales**

Crea un archivo `.streamlit/secrets.toml` en la raíz del proyecto:

```toml
OPENAI_API_KEY = "tu-clave-api-aqui"
EMAIL_USER = "tu-email@gmail.com"
EMAIL_PASSWORD = "tu-contraseña-de-aplicacion"
```

> **Nota sobre Gmail**: Usa [contraseña de aplicación](https://support.google.com/accounts/answer/185833) en lugar de tu contraseña de Gmail.

5. **Ejecutar la aplicación**
```bash
streamlit run app.py
```

La aplicación estará disponible en `http://localhost:8501`

## 📚 Estructura del Proyecto

```
Proyecto_Economica/
├── app.py                          # Aplicación principal (Streamlit)
├── requirements.txt                # Dependencias del proyecto
├── README.md                       # Este archivo
├── .gitignore                      # Archivos a ignorar en Git
├── .streamlit/
│   └── secrets.toml               # Configuración (NO versionar)
├── modules/
│   ├── __init__.py
│   ├── bond_comparables.py        # Datos y funciones de bonos
│   ├── chatbot_assistant.py       # Asistente IA conversacional
│   ├── fx_converter.py            # Motor de conversión de monedas
│   ├── fx_ui.py                   # UI del conversor FX (Streamlit)
│   ├── market_comparison_ui.py    # Interfaz de comparación de mercado
│   ├── market_data.py             # Integración Yahoo Finance
│   ├── presets.py                 # Plantillas predefinidas
│   ├── user_data.py               # Gestión de datos de usuario
│   └── __pycache__/               # Caché de Python (NO versionar)
├── telegram/
│   └── qr_contacto.png            # Código QR de contacto
└── __pycache__/                   # Caché de Python (NO versionar)
```

## 🔧 Módulos Principales

### `app.py`
Aplicación principal que integra todas las funcionalidades:
- Interfaz de usuario con Streamlit
- Lógica de cálculo financiero
- Gestión de temas y estilos
- Generación de PDFs y emails

### `modules/bond_comparables.py`
Sistema de comparación de bonos:
- Base de datos de bonos de referencia (Tesoro USA, Corporativos, etc.)
- Función de clasificación de spreads
- Búsqueda de comparables más cercanos
- Análisis de riesgo/retorno

### `modules/market_data.py`
Integración con Yahoo Finance:
- Obtención de datos históricos de acciones
- Cálculo de CAGR (Compound Annual Growth Rate)
- Análisis de volatilidad
- Comparativa simulación vs. mercado real

### `modules/chatbot_assistant.py`
Asistente financiero con IA:
- Inicialización de sesiones de chat
- Gestión del historial de mensajes
- Contexto dinámico de usuario
- Interfaz compacta y completa

### `modules/fx_converter.py`
Motor de conversión de monedas (FX):
- Obtención de tasas desde API gratuita (open.er-api.com)
- Clase `FXCache` para gestión inteligente de cache con TTL y persistencia JSON
- Soporte para 45+ monedas (todas las latinoamericanas prioritarias)
- Tasas spot (tiempo real) con validación de códigos ISO 4217
- Retry automático con backoff exponencial (máx 3 intentos, 1s-2s-4s)
- Excepciones personalizadas: `UnsupportedCurrencyError`, `RateNotFoundError`, `ProviderError`
- Logging completo para auditoría y debugging
- Funciones públicas: `get_fx_rate()`, `convert_currency()`, `is_valid_currency()`, `get_supported_currencies()`

### `modules/fx_ui.py`
Interfaz Streamlit del conversor FX:
- Widget interactivo `show_fx_converter_widget()` con conversión en tiempo real
- Entrada de monto personalizable con validación
- Selectores de monedas con indexación dinámica
- Botón "↔️ Invertir" para intercambiar monedas origen/destino
- **Panel dinámico de tasas**: muestra 10 monedas relevantes vs. moneda de referencia
- Indicadores visuales de fuente (🔴 API en tiempo real, 🟡 Cache, 🟢 Manual)
- Visualización de última conversión realizada con métricas
- Opciones avanzadas: tasa manual (fallback), limpiar cache
- Manejo robusto de errores con mensajes intuitivos
- Integración perfecta con `fx_converter.py` y session_state de Streamlit

### `modules/market_comparison_ui.py`
Componente UI para comparaciones:
- Búsqueda de acciones
- Validación de tickers
- Gráficos comparativos interactivos
- Información de empresas

### `modules/presets.py`
Plantillas predefinidas para inicio rápido:
- Presets de acciones (Conservador, Balanceado, Agresivo)
- Presets de bonos (Seguros, Rentables, Emergentes)

### `modules/user_data.py`
Gestión de datos y persistencia:
- Almacenamiento de simulaciones
- Exportación/importación JSON
- Sistema de escenarios comparables
- Historial de usuario

## 📖 Guía de Uso

### Simulación de Acciones

1. **Ingresa parámetros**:
   - Inversión inicial
   - Aportes periódicos (opcional)
   - Plazo en años
   - TEA esperado (%)
   - Dividendo anual (%)

2. **Ejecuta la simulación** y visualiza:
   - Valor futuro total
   - Ganancia neta
   - Dividendos proyectados
   - Gráfico de crecimiento

3. **Compara con mercado real**:
   - Ingresa ticker (ej: AAPL, MSFT)
   - Visualiza CAGR histórico
   - Analiza volatilidad

### Análisis de Bonos

1. **Define características del bono**:
   - Valor nominal
   - Tasa de cupón
   - TEA (rendimiento esperado)
   - Período de cupón
   - Cantidad de períodos

2. **Obtén análisis**:
   - Valor presente justo
   - Clasificación del spread
   - Bonos comparables
   - Evaluación de riesgo

### Conversor de Monedas (FX)

1. **Accede a la pestaña "💱 Conversor FX"**

2. **Ingresa parámetros de conversión**:
   - Monto a convertir (ej: 100)
   - Moneda origen (ej: PEN - Sol Peruano)
   - Moneda destino (ej: USD - Dólar)

3. **Realiza la conversión**:
   - Presiona "🔄 Convertir" para obtener tasa en tiempo real
   - Visualiza tasa aplicada y timestamp
   - Verifica fuente de la tasa en indicador (🔴 API | 🟡 Cache | 🟢 Manual)
   - Observa resultado con formula de cálculo

4. **Funciones avanzadas**:
   - **↔️ Invertir**: Intercambia moneda origen/destino con un clic
   - **Tasa manual**: Si API falla, proporciona fallback manual
   - **Limpiar cache**: Fuerza actualización de tasas desde API
   - **Moneda de referencia**: Selector para panel dinámico de tasas

5. **Panel de tasas relevantes**:
   - Muestra tasa de 10 monedas importantes vs. tu moneda de referencia
   - Útil para comparar múltiples conversiones simultáneamente
   - Cada tasa incluye indicador de fuente

6. **Monedas soportadas** (45+ opciones):
   
   **Latinoamericanas (Prioritarias):**
   - �� **PEN** - Sol Peruano ⭐
   - �� **ARS** - Peso Argentino
   - 🇧🇷 **BRL** - Real Brasileño
   - 🇨🇱 **CLP** - Peso Chileno
   - 🇨🇴 **COP** - Peso Colombiano
   - �� **MXN** - Peso Mexicano
   - 🇺🇾 **UYU** - Peso Uruguayo
   - 🇻🇪 **VES** - Bolívar Venezolano
   
   **Principales:**
   - 🇺🇸 **USD** - Dólar Estadounidense
   - 🇪🇺 **EUR** - Euro
   - 🇬🇧 **GBP** - Libra Esterlina
   - 🇯🇵 **JPY** - Yen Japonés
   - 🇨🇭 **CHF** - Franco Suizo
   - 🇨🇦 **CAD** - Dólar Canadiense
   
   **Y 30+ más** (AUD, NZD, SGD, HKD, CNY, INR, THB, KRW, SEK, NOK, DKK, etc.)

### Consulta con IA

1. **Realiza una simulación** (Acciones o Bonos)
2. **Abre el chat** en la pestaña "💬 Chatbot IA"
3. **Formúlale preguntas** como:
   - "¿Mi proyección es realista?"
   - "Explícame qué es el TEA"
   - "¿Conviene retirar todo o solo dividendos?"

## 🔑 Variables de Entorno

La aplicación requiere configuración en `.streamlit/secrets.toml`:

| Variable | Descripción | Ejemplo |
|----------|-----------|---------|
| `OPENAI_API_KEY` | Clave API de OpenAI | `sk-proj-...` |
| `EMAIL_USER` | Email para envío de reportes | `user@gmail.com` |
| `EMAIL_PASSWORD` | Contraseña de aplicación Gmail | `xxxx xxxx xxxx xxxx` |

## 📊 Fórmulas Financieras

### Valor Futuro (Acciones)
```
VF = PV × (1 + r)ⁿ + Anualidad × [((1 + r)ⁿ - 1) / r]

Donde:
- PV = Valor presente (inversión inicial)
- r = Tasa de interés periódica
- n = Número de períodos
```

### Valor Presente de Bono (PV)
```
PV = Σ [C / (1 + y)ᵗ] + FV / (1 + y)ⁿ

Donde:
- C = Flujo de cupón
- y = Rendimiento periódico (TEA)
- FV = Valor nominal
- n = Número de períodos
```

### CAGR (Tasa Anual Compuesta)
```
CAGR = (Valor Final / Valor Inicial)^(1/n) - 1

Donde:
- n = Número de años
```

## ⚠️ Limitaciones y Consideraciones

- 📋 **No es recomendación de inversión**: Esta herramienta es educativa y analítica
- 📊 **Datos históricos**: Yahoo Finance (últimos 5 años por defecto)
- 🎲 **Rendimientos futuros**: No garantizados, el pasado no asegura futuro
- 💰 **Comisiones e impuestos**: No incluidos en cálculos
- 🌐 **Conexión**: Requiere internet para datos de mercado real

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios importantes:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcion`)
3. Commit tus cambios (`git commit -am 'Agrega nueva función'`)
4. Push a la rama (`git push origin feature/nueva-funcion`)
5. Abre un Pull Request

## � Autores

Este proyecto fue desarrollado colaborativamente por:

- **Cuba Moya, Diego Joel**
- **López Malca, Steven**
- **Polonio Ramos, Franco Imanol**
- **Sánchez Vásquez, Anthony**
- **Zanabria Yrigoin, Gaby Lizeth**

## �📄 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo [LICENSE](LICENSE) para más detalles.

## 🙋 Soporte y Contacto

- � **WhatsApp**: Escanea el código QR en la aplicación para contactar directamente con soporte técnico
- 🐛 **Reporte de bugs**: Abre un issue en GitHub
- 💡 **Sugerencias**: Discusiones en GitHub
- 📱 **Disponibilidad**: Soporte técnico a través de WhatsApp

## 🚨 Soporte de Emergencia

Si la aplicación presenta **errores o fallos**, puedes contactar al equipo de soporte técnico de inmediato:

1. **Escanea el código QR** que aparece en la parte inferior de la aplicación
2. **Se abrirá automáticamente WhatsApp** con el número de soporte técnico
3. **Describe el problema** brevemente y un asesor lo resolverá lo antes posible

> ⚠️ **Nota importante**: El código QR es tu principal canal de contacto rápido para asuntos urgentes. Te lleva directamente a WhatsApp de soporte técnico disponible 24/7.

## �📚 Recursos Adicionales

- [Documentación Streamlit](https://docs.streamlit.io)
- [Yahoo Finance API](https://finance.yahoo.com)
- [OpenAI API](https://platform.openai.com/docs)
- [Educación Financiera (Investopedia)](https://www.investopedia.com)

## 🎓 Glosario Financiero

| Término | Descripción |
|---------|-----------|
| **TEA** | Tasa Efectiva Anual - rendimiento anualizado |
| **CAGR** | Tasa de Crecimiento Anual Compuesta |
| **PV** | Valor Presente (Present Value) |
| **FV** | Valor Futuro (Future Value) |
| **Cupón** | Pago periódico de intereses de un bono |
| **Spread** | Diferencia de rendimiento entre dos instrumentos |
| **Volatilidad** | Medida de riesgo (desviación estándar de retornos) |
| **CAGR** | Rendimiento anualizado compuesto |

---

**Última actualización**: Noviembre 2025  
**Versión**: 1.0.0  
**Equipo de desarrollo**:
