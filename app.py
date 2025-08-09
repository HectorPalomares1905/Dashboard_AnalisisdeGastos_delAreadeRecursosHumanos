import dash
from dash import html, dcc, Input, Output
import plotly.graph_objects as go
import pandas as pd
import os
from funciones import (
    cargar_datos,
    calcular_metricas,
    crear_grafico_velocimetro,
    crear_grafico_barras_categoria,
    crear_grafico_lineas_mes,
    crear_tabla_matriz,
    crear_grafico_anillo_semestre,
    crear_grafico_columnas_trimestre,
    crear_grafico_radar_eficiencia
)

# Inicializar la aplicación Dash con configuración de assets
app = dash.Dash(__name__, 
                assets_folder='assets',
                assets_url_path='/assets',
                suppress_callback_exceptions=True)

# Importante para Render.com
server = app.server

# Cargar y procesar los datos
df_gastos, df_presupuesto, df_calendario, df_consolidado = cargar_datos()

# Calcular métricas principales
total_gastado, total_presupuesto, saldo, porcentaje_gasto = calcular_metricas(df_consolidado)

# Layout de la aplicación
app.layout = html.Div([
    # Header
    html.Div([
        html.H1('Dashboard de Análisis de Gastos del Área de Recursos Humanos', 
                className='dashboard-title'),
        html.Div('Enero - Agosto de 2019', className='dashboard-subtitle')
    ], className='header'),
    
    # Contenedor principal
    html.Div([
        # Fila superior con métricas principales
        html.Div([
            # Columna izquierda - Velocímetro con contenedor fijo
            html.Div([
                html.Div([
                    dcc.Graph(
                        id='velocimetro',
                        figure=crear_grafico_velocimetro(total_gastado, total_presupuesto),
                        className='gauge-chart',
                        config={'displayModeBar': False, 'responsive': True}
                    )
                ], style={'height': '220px', 'width': '100%', 'position': 'relative', 'overflow': 'hidden'})
            ], className='metric-card-large gauge-container'),
            
            # Columnas de métricas - usando iconos con CSS en lugar de imágenes
            html.Div([
                html.Div('📊', className='metric-icon-emoji'),
                html.H2(f'{porcentaje_gasto:.1f} %', className='metric-value'),
                html.P('% DE GASTO', className='metric-label')
            ], className='metric-card-large'),
            
            html.Div([
                html.Div('💰', className='metric-icon-emoji'),
                html.H2(f'{saldo:,.0f}', className='metric-value'),
                html.P('SALDO', className='metric-label')
            ], className='metric-card-large'),
            
            html.Div([
                html.Div('💵', className='metric-icon-emoji'),
                html.H2(f'{total_presupuesto:,.0f}', className='metric-value'),
                html.P('TOTAL PRESUPUESTO', className='metric-label')
            ], className='metric-card-large')
        ], className='top-section'),
        
        # Segunda fila - Gráficos principales
        html.Div([
            # Gráfico de barras - Total por categoría
            html.Div([
                html.H3('Total Gastado por Categoría', className='chart-title'),
                dcc.Graph(
                    id='grafico-categorias',
                    figure=crear_grafico_barras_categoria(df_consolidado),
                    config={'displayModeBar': False}
                )
            ], className='chart-container col-3'),
            
            # Gráfico de líneas - Total por mes
            html.Div([
                html.H3('Total Gastado por Mes', className='chart-title'),
                dcc.Graph(
                    id='grafico-meses',
                    figure=crear_grafico_lineas_mes(df_consolidado),
                    config={'displayModeBar': False}
                )
            ], className='chart-container col-4'),
            
            # Gráfico de anillo - Por semestre
            html.Div([
                html.H3('Total Gastado por Semestre', className='chart-title'),
                dcc.Graph(
                    id='grafico-semestre',
                    figure=crear_grafico_anillo_semestre(df_consolidado),
                    config={'displayModeBar': False}
                )
            ], className='chart-container col-2')
        ], className='middle-section'),
        
        # Tercera fila - Tabla y gráficos
        html.Div([
            # Tabla matriz
            html.Div([
                html.H3('Detalle por Categoría', className='chart-title'),
                html.Div(
                    id='tabla-matriz',
                    children=crear_tabla_matriz(df_consolidado)
                )
            ], className='table-container'),
            
            # Contenedor para los dos gráficos del lado derecho
            html.Div([
                # Gráfico de columnas - Por trimestre
                html.Div([
                    html.H3('Total Gastado por Trimestre', className='chart-title'),
                    dcc.Graph(
                        id='grafico-trimestre',
                        figure=crear_grafico_columnas_trimestre(df_consolidado),
                        config={'displayModeBar': False}
                    )
                ], className='chart-container-half'),
                
                # Nuevo gráfico de radar - Eficiencia del presupuesto
                html.Div([
                    html.H3('Eficiencia del Presupuesto', className='chart-title'),
                    dcc.Graph(
                        id='grafico-radar',
                        figure=crear_grafico_radar_eficiencia(df_consolidado),
                        config={'displayModeBar': False}
                    )
                ], className='chart-container-half')
            ], className='right-charts-container')
        ], className='bottom-section')
    ], className='main-container')
], className='dashboard')

# Callback para actualizar el dashboard
@app.callback(
    Output('velocimetro', 'figure'),
    Input('velocimetro', 'id')
)
def update_gauge(id):
    return crear_grafico_velocimetro(total_gastado, total_presupuesto)

if __name__ == '__main__':
    # Obtener el puerto de la variable de entorno para Render
    port = int(os.environ.get('PORT', 8050))
    # En producción, usar host='0.0.0.0' para que sea accesible externamente
    app.run_server(debug=False, host='0.0.0.0', port=port)
