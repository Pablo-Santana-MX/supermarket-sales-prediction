import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from prophet import Prophet
import pulp
from pathlib import Path

# --- 1. Configuración de la Página ---
st.set_page_config(page_title="Supermarket Sales Dashboard", page_icon="🛒", layout="wide")

# --- 2. Gestor de Idiomas (Estado de Sesión) ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'ES'  # Idioma por defecto

def t(es_text, en_text):
    """Función maestra de traducción. Devuelve el texto según el idioma seleccionado."""
    return es_text if st.session_state.lang == 'ES' else en_text

# --- 3. Resolución Dinámica de Rutas ---
BASE_DIR = Path(__file__).parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "supermarket_analysis_clean.csv"

# --- 4. Funciones Principales ---
@st.cache_data
def load_data(file_path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(t(f"Datos no encontrados en {file_path}.", f"Data not found at {file_path}."))
        st.stop()

@st.cache_data
def generate_forecast(df: pd.DataFrame, days: int = 30) -> tuple:
    df['date'] = pd.to_datetime(df['date'])
    daily_sales = df.groupby('date')['sales'].sum().reset_index()
    prophet_df = daily_sales.rename(columns={'date': 'ds', 'sales': 'y'})
    
    model = Prophet(interval_width=0.95, daily_seasonality=False)
    model.fit(prophet_df)
    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)
    return prophet_df, forecast

def run_optimization(budget: float, space: float) -> tuple:
    data = {
        'product_line': ['Health and beauty', 'Electronic accessories', 'Home and lifestyle', 'Sports and travel', 'Food and beverages', 'Fashion accessories'],
        'unit_cost': [25.0, 55.0, 40.0, 35.0, 10.0, 30.0],
        'unit_profit': [8.0, 15.0, 12.0, 10.0, 3.0, 9.0],
        'unit_volume': [0.05, 0.15, 0.50, 0.30, 0.10, 0.08],
        'max_demand': [500, 300, 400, 450, 1200, 600] 
    }
    df_inv = pd.DataFrame(data)
    
    prob = pulp.LpProblem("Inventory_Optimization", pulp.LpMaximize)
    products = df_inv['product_line'].tolist()
    x = pulp.LpVariable.dicts("units", products, lowBound=0, cat='Integer')
    
    prob += pulp.lpSum([df_inv.loc[df_inv['product_line'] == p, 'unit_profit'].values[0] * x[p] for p in products])
    prob += pulp.lpSum([df_inv.loc[df_inv['product_line'] == p, 'unit_cost'].values[0] * x[p] for p in products]) <= budget
    prob += pulp.lpSum([df_inv.loc[df_inv['product_line'] == p, 'unit_volume'].values[0] * x[p] for p in products]) <= space
    
    for p in products:
        max_d = df_inv.loc[df_inv['product_line'] == p, 'max_demand'].values[0]
        prob += x[p] <= max_d
        
    prob.solve()
    
    if pulp.LpStatus[prob.status] == 'Optimal':
        results = [{'product_line': p, 'optimal_units': x[p].varValue} for p in products]
        res_df = pd.DataFrame(results)
        final_df = pd.merge(df_inv, res_df, on='product_line')
        final_df['total_cost'] = final_df['unit_cost'] * final_df['optimal_units']
        final_df['projected_profit'] = final_df['unit_profit'] * final_df['optimal_units']
        return final_df, True
    return None, False

# Cargar datos
df = load_data(DATA_PATH)

# --- 5. Encabezado y Selector de Idioma (Arriba a la derecha) ---
col_title, col_lang = st.columns([85, 15])
with col_title:
    st.title(t("📊 Rendimiento del Supermercado", "📊 Supermarket Performance"))
with col_lang:
    st.radio("🌐 Idioma / Language", ["ES", "EN"], horizontal=True, key="lang", label_visibility="collapsed")

# --- 6. Barra Lateral ---
st.sidebar.header(t("⚙️ Filtros", "⚙️ Filters"))
branch_filter = st.sidebar.multiselect(t("Sucursal", "Branch"), options=df["branch"].unique(), default=df["branch"].unique())
product_filter = st.sidebar.multiselect(t("Línea de Producto", "Product Line"), options=df["product_line"].unique(), default=df["product_line"].unique())
customer_filter = st.sidebar.multiselect(t("Tipo de Cliente", "Customer Type"), options=df["customer_type"].unique(), default=df["customer_type"].unique())
gender_filter = st.sidebar.multiselect(t("Género", "Gender"), options=df["gender"].unique(), default=df["gender"].unique())

df_filtered = df[
    (df["branch"].isin(branch_filter)) & (df["product_line"].isin(product_filter)) &
    (df["customer_type"].isin(customer_filter)) & (df["gender"].isin(gender_filter))
]

st.sidebar.markdown("---")
st.sidebar.subheader(t("💾 Exportar Datos", "💾 Export Data"))
st.sidebar.download_button(
    label=t("⬇️ Descargar CSV", "⬇️ Download CSV"), 
    data=df_filtered.to_csv(index=False).encode('utf-8'), 
    file_name='filtered_supermarket_data.csv', 
    mime='text/csv'
)

# --- 7. Contenido Principal ---
with st.expander(t("📖 Cómo usar este dashboard", "📖 How to use this dashboard")):
    st.markdown(t(
        "Filtra los datos a la izquierda. Revisa las tendencias históricas abajo y explora las pestañas de **Pronóstico (Prophet)** y **Optimización (PuLP)** en la parte inferior para inteligencia avanzada.",
        "Filter data on the left. Review historical trends below and explore the **Forecasting (Prophet)** and **Optimization (PuLP)** tabs at the bottom for advanced intelligence."
    ))

if df_filtered.empty:
    st.warning(t("No hay datos para esta combinación de filtros.", "No data available for these filters."))
    st.stop()

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(t("Ingresos Totales", "Total Revenue"), f"${df_filtered['sales'].sum():,.2f}")
kpi2.metric(t("Ticket Promedio", "Average Ticket"), f"${df_filtered['sales'].mean():,.2f}")
kpi3.metric(t("Transacciones Totales", "Total Transactions"), f"{len(df_filtered):,}")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    fig_branch = px.bar(
        df_filtered.groupby(['branch', 'city'])['sales'].sum().reset_index(), 
        x='branch', y='sales', color='city', color_discrete_sequence=px.colors.qualitative.Prism, 
        title=t("Ingresos por Sucursal", "Revenue by Branch")
    )
    st.plotly_chart(fig_branch, use_container_width=True)
with col2:
    fig_income = px.bar(
        df_filtered.groupby('product_line')['gross_income'].sum().reset_index().sort_values(by='gross_income'), 
        x='gross_income', y='product_line', orientation='h', color_continuous_scale=px.colors.sequential.Teal, 
        color='gross_income', title=t("Mejor Ingreso Bruto", "Top Gross Income")
    )
    st.plotly_chart(fig_income, use_container_width=True)

st.markdown("---")

# --- 8. Pestañas de Analítica Avanzada ---
tab1, tab2 = st.tabs([t("🔮 Fase 2: Pronóstico (Prophet)", "🔮 Phase 2: Forecasting (Prophet)"), t("📦 Fase 3: Optimización (PuLP)", "📦 Phase 3: Optimization (PuLP)")])

with tab1:
    st.subheader(t("Pronóstico de Ventas a 30 Días", "30-Day Sales Forecast"))
    historic, forecast = generate_forecast(df_filtered) 
    fig_forecast = go.Figure()
    fig_forecast.add_trace(go.Scatter(x=historic['ds'], y=historic['y'], mode='markers+lines', name=t('Reales', 'Actual'), line=dict(color='black')))
    fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name=t('Pronóstico', 'Forecast'), line=dict(color='blue')))
    fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], mode='lines', line=dict(width=0), showlegend=False))
    fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], mode='lines', line=dict(width=0), fillcolor='rgba(0, 0, 255, 0.2)', fill='tonexty', name=t('95% Confianza', '95% Confidence')))
    fig_forecast.update_layout(hovermode='x unified', template="plotly_white")
    st.plotly_chart(fig_forecast, use_container_width=True)

with tab2:
    st.subheader(t("Asignación de Inventario Inteligente", "Intelligent Inventory Allocation"))
    st.markdown(t("Ajusta las restricciones para calcular el plan de compra perfecto.", "Adjust constraints to calculate the perfect purchase plan."))
    
    opt_col1, opt_col2 = st.columns(2)
    user_budget = opt_col1.slider(t("💰 Presupuesto Máximo ($)", "💰 Max Budget ($)"), min_value=5000.0, max_value=50000.0, value=30000.0, step=1000.0)
    user_space = opt_col2.slider(t("📦 Espacio Máximo (m³)", "📦 Max Space (m³)"), min_value=50.0, max_value=500.0, value=200.0, step=10.0)
    
    if st.button(t("🚀 Ejecutar Optimización", "🚀 Run Optimization")):
        with st.spinner(t("Calculando modelo matemático...", "Computing mathematical model...")):
            opt_df, success = run_optimization(user_budget, user_space)
            
            if success:
                st.success(t("¡Solución Óptima Encontrada!", "Optimal Solution Found!"))
                st.dataframe(opt_df[['product_line', 'optimal_units', 'total_cost', 'projected_profit']].style.format({'optimal_units': '{:.0f}', 'total_cost': '${:.2f}', 'projected_profit': '${:.2f}'}), use_container_width=True)
                
                fig_opt = px.pie(opt_df[opt_df['optimal_units'] > 0], values='optimal_units', names='product_line', title=t('Distribución de Compra Sugerida', 'Suggested Purchase Distribution'), hole=0.4)
                st.plotly_chart(fig_opt, use_container_width=True)
                
                st.metric(t("🏆 Ganancia Máxima Proyectada", "🏆 Max Projected Profit"), f"${opt_df['projected_profit'].sum():,.2f}")
            else:
                st.error(t("No se encontró solución con estos parámetros.", "Could not find a solution with these parameters."))

st.markdown("---")

# --- 9. Autoría Condicional por Idioma ---
if st.session_state.lang == 'ES':
    st.markdown("""
    ## 👤 Científico de Datos Aplicado e Investigador
    **Pablo Alberto Santana Flores**  
    *Ingeniero Químico | PhD candidate in Marine Sciences | Inteligencia de Decisiones*  

    > Gracias por explorar el **Motor Dinámico de Predicción de Ventas**. Esta aplicación interactiva exhibe las fases *Descriptiva* (EDA), *Predictiva* (Prophet) y *Prescriptiva* (PuLP) de un pipeline analítico de extremo a extremo. Siéntete libre de conectar en LinkedIn para discutir la arquitectura técnica.

    *   **LinkedIn:** [linkedin.com/in/pablo-santana-mx](https://mx.linkedin.com/in/pablo-santana-mx)
    *   **GitHub:** [github.com/Pablo-Santana-MX](https://github.com/Pablo-Santana-MX)
    """)
else:
    st.markdown("""
    ## 👤 Applied Data Scientist & Researcher
    **Pablo Alberto Santana Flores**  
    *Chemical Engineer | PhD in Marine Sciences | Decision Intelligence*  

    > Thank you for exploring the **Dynamic Sales Prediction Engine**. This interactive application showcases the *Descriptive* (EDA), *Predictive* (Prophet), and *Prescriptive* (PuLP) phases of an end-to-end analytical pipeline. Feel free to connect on LinkedIn to discuss the technical architecture.  

    *   **LinkedIn:** [linkedin.com/in/pablo-santana-mx](https://mx.linkedin.com/in/pablo-santana-mx)
    *   **GitHub:** [github.com/Pablo-Santana-MX](https://github.com/Pablo-Santana-MX)
    """)