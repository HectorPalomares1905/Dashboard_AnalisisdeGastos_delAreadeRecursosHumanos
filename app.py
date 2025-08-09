import dash
from dash import html, dcc, Input, Output
import plotly.graph_objects as go
import pandas as pd
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

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

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
            # Columna izquierda - Velocímetro
            html.Div([
                dcc.Graph(
                    id='velocimetro',
                    figure=crear_grafico_velocimetro(total_gastado, total_presupuesto),
                    className='gauge-chart',
                    config={'displayModeBar': False, 'responsive': True},
                    style={'height': '240px', 'width': '100%'}
                )
            ], className='metric-card-large gauge-container'),
            
            # Columnas de métricas - mismo tamaño que el velocímetro
            html.Div([
                html.Img(src='/assets/images/percentage-icon.png', className='metric-icon'),
                html.H2(f'{porcentaje_gasto:.1f} %', className='metric-value'),
                html.P('% DE GASTO', className='metric-label')
            ], className='metric-card-large'),
            
            html.Div([
                html.Img(src='/assets/images/budget-icon.png', className='metric-icon'),
                html.H2(f'{saldo:,.0f}', className='metric-value'),
                html.P('SALDO', className='metric-label')
            ], className='metric-card-large'),
            
            html.Div([
                html.Img(src='/assets/images/money-icon.png', className='metric-icon'),
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
                    figure=crear_grafico_barras_categoria(df_consolidado)
                )
            ], className='chart-container col-3'),
            
            # Gráfico de líneas - Total por mes
            html.Div([
                html.H3('Total Gastado por Mes', className='chart-title'),
                dcc.Graph(
                    id='grafico-meses',
                    figure=crear_grafico_lineas_mes(df_consolidado)
                )
            ], className='chart-container col-4'),
            
            # Gráfico de anillo - Por semestre
            html.Div([
                html.H3('Total Gastado por Semestre', className='chart-title'),
                dcc.Graph(
                    id='grafico-semestre',
                    figure=crear_grafico_anillo_semestre(df_consolidado)
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

# Callback para actualizar el dashboard (si necesitas interactividad futura)
@app.callback(
    Output('velocimetro', 'figure'),
    Input('velocimetro', 'id')
)
def update_gauge(id):
    return crear_grafico_velocimetro(total_gastado, total_presupuesto)

if __name__ == '__main__':

    app.run(debug=True)
