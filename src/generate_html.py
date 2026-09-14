import pandas as pd
import plotly.express as px

def generar_dashboard():
    print("Cargando el dataset...")
    # Asegúrate de que el nombre del CSV coincida con el que descargaste
    ruta_csv = "../data/raw/supermarket_sales - Sheet1.csv"
    df = pd.read_csv(ruta_csv)

    print("Calculando métricas y generando gráficas...")
    
    # Gráfica 1: ¿Qué línea de productos genera más ingresos?
    ventas_por_linea = df.groupby('Product line')['Total'].sum().reset_index()
    fig1 = px.bar(
        ventas_por_linea, 
        x='Total', 
        y='Product line', 
        orientation='h',
        title='Ingresos Totales por Línea de Producto',
        color='Product line'
    )

    # Gráfica 2: ¿Cómo prefieren pagar los clientes?
    pagos = df['Payment'].value_counts().reset_index()
    fig2 = px.pie(
        pagos, 
        names='Payment', 
        values='count', 
        title='Distribución de Métodos de Pago',
        hole=0.4
    )

    print("Ensamblando el archivo web...")
    
    # Extraer los bloques de HTML de cada gráfica
    # Solo cargamos la librería de Plotly (CDN) en la primera gráfica para optimizar peso
    html_fig1 = fig1.to_html(full_html=False, include_plotlyjs='cdn')
    html_fig2 = fig2.to_html(full_html=False, include_plotlyjs=False)

    # Estructura del sitio web
    html_template = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Dashboard de Ventas</title>
        <style>
            body {{ font-family: sans-serif; background-color: #f8f9fa; padding: 20px; }}
            .container {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; }}
            .card {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 45%; min-width: 400px; }}
            h1 {{ text-align: center; color: #333; }}
        </style>
    </head>
    <body>
        <h1>📊 Dashboard de Ventas del Supermercado</h1>
        <div class="container">
            <div class="card">{html_fig1}</div>
            <div class="card">{html_fig2}</div>
        </div>
    </body>
    </html>
    """

    # Guardar en la carpeta outputs
    ruta_salida = "../outputs/dashboard_interactivo.html"
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(html_template)

    print(f"¡Éxito! Dashboard generado en: {ruta_salida}")

if __name__ == "__main__":
    generar_dashboard()