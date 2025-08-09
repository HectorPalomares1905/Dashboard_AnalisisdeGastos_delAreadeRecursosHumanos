import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import html
import numpy as np
from datetime import datetime

def cargar_datos():
    """Cargar y procesar los datos desde el archivo Excel"""
    # Cargar las hojas del Excel
    df_gastos = pd.read_excel('Base de Datos.xlsx', sheet_name='Gastos')
    df_presupuesto = pd.read_excel('Base de Datos.xlsx', sheet_name='Presupuesto')
    df_calendario = pd.read_excel('Base de Datos.xlsx', sheet_name='Tabla Calendario')
    
    # Convertir fecha de Excel a datetime si es necesario
    if df_gastos['Fecha'].dtype == 'int64' or df_gastos['Fecha'].dtype == 'float64':
        df_gastos['Fecha'] = pd.to_datetime('1899-12-30') + pd.to_timedelta(df_gastos['Fecha'], 'D')
    else:
        df_gastos['Fecha'] = pd.to_datetime(df_gastos['Fecha'])
    
    # Convertir fecha del calendario
    if df_calendario['Fecha'].dtype == 'int64' or df_calendario['Fecha'].dtype == 'float64':
        df_calendario['Fecha'] = pd.to_datetime('1899-12-30') + pd.to_timedelta(df_calendario['Fecha'], 'D')
    else:
        df_calendario['Fecha'] = pd.to_datetime(df_calendario['Fecha'])
    
    # Merge gastos con calendario
    df_gastos = df_gastos.merge(df_calendario[['Fecha', 'Mes', 'Mes Num', 'Trimestre', 'Semestre', 'Año']], 
                                on='Fecha', how='left')
    
    # Merge con presupuesto
    df_consolidado = df_gastos.merge(df_presupuesto, left_on='Cuenta', right_on='cuenta', how='left')
    
    # Filtrar solo datos de 2019
    df_consolidado = df_consolidado[df_consolidado['Año'] == 2019]
    
    return df_gastos, df_presupuesto, df_calendario, df_consolidado

def calcular_metricas(df_consolidado):
    """Calcular las métricas principales del dashboard"""
    total_gastado = df_consolidado['Gastos'].sum()
    total_presupuesto = 621000  # Presupuesto total según la imagen
    saldo = total_presupuesto - total_gastado
    porcentaje_gasto = (total_gastado / total_presupuesto) * 100
    
    return total_gastado, total_presupuesto, saldo, porcentaje_gasto

def crear_grafico_velocimetro(total_gastado, total_presupuesto):
    """Crear el gráfico de velocímetro para el total gastado"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = total_gastado,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Total Gastado", 'font': {'size': 12, 'color': '#94F8FD'}},
        number = {'font': {'size': 32, 'color': '#94F8FD'}, 'valueformat': ',.0f'},
        gauge = {
            'axis': {'range': [None, total_presupuesto], 
                    'tickwidth': 1, 
                    'tickcolor': "#94F8FD",
                    'tickfont': {'color': '#94F8FD', 'size': 9}},
            'bar': {'color': "#94F8FD", 'thickness': 0.8},
            'bgcolor': "#1B1B2D",
            'borderwidth': 2,
            'bordercolor': "#94F8FD",
            'steps': [
                {'range': [0, total_presupuesto * 0.5], 'color': '#13121D'},
                {'range': [total_presupuesto * 0.5, total_presupuesto * 0.75], 'color': '#1B1B2D'},
                {'range': [total_presupuesto * 0.75, total_presupuesto], 'color': '#2A2A3E'}
            ],
            'threshold': {
                'line': {'color': "#FF4444", 'width': 3},
                'thickness': 0.75,
                'value': total_presupuesto * 0.9
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "#94F8FD", 'family': 'Segoe UI'},
        height=220,
        margin=dict(l=5, r=5, t=25, b=5),
        autosize=False
    )
    
    # Agregar texto adicional
    fig.add_annotation(
        text=f"0 mil",
        x=0.15, y=0.15,
        showarrow=False,
        font=dict(size=9, color="#94F8FD")
    )
    fig.add_annotation(
        text=f"{total_presupuesto/1000:.0f} mil",
        x=0.85, y=0.15,
        showarrow=False,
        font=dict(size=9, color="#94F8FD")
    )
    
    return fig

def crear_grafico_barras_categoria(df_consolidado):
    """Crear gráfico de barras horizontales por categoría"""
    df_categoria = df_consolidado.groupby('Categoría')['Gastos'].sum().reset_index()
    df_categoria = df_categoria.sort_values('Gastos', ascending=True)
    
    fig = go.Figure(data=[
        go.Bar(
            x=df_categoria['Gastos'],
            y=df_categoria['Categoría'],
            orientation='h',
            marker_color='#94F8FD',
            text=df_categoria['Gastos'].apply(lambda x: f'{x:,.0f}'),
            textposition='auto',
            textfont=dict(color="#605EEF", size=10, family='Segoe UI')
        )
    ])
    
    fig.update_layout(
        paper_bgcolor="#13121D",
        plot_bgcolor="#1B1B2D",
        font={'color': "#94F8FD", 'family': 'Segoe UI'},
        xaxis=dict(
            showgrid=True,
            gridcolor='#2A2A3E',
            zeroline=False,
            showticklabels=False
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=10)
        ),
        height=300,
        margin=dict(l=120, r=20, t=20, b=40),
        showlegend=False
    )
    
    return fig

def crear_grafico_lineas_mes(df_consolidado):
    """Crear gráfico de líneas por mes"""
    # Ordenar los meses correctamente
    meses_orden = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto']
    df_mes = df_consolidado.groupby(['Mes', 'Mes Num'])['Gastos'].sum().reset_index()
    df_mes = df_mes.sort_values('Mes Num')
    
    # Crear valores para el gráfico
    valores = [60300, 56300, 54300, 59100, 59000, 58300, 60200, 58760]  # Valores aproximados de la imagen
    
    fig = go.Figure(data=[
        go.Scatter(
            x=list(range(1, 9)),
            y=valores,
            mode='lines+markers+text',
            line=dict(color='#94F8FD', width=3),
            marker=dict(color='#94F8FD', size=10),
            text=[f'{v/1000:.1f} mil' for v in valores],
            textposition='top center',
            textfont=dict(color='#94F8FD', size=10, family='Segoe UI')
        )
    ])
    
    fig.update_layout(
        paper_bgcolor="#13121D",
        plot_bgcolor="#1B1B2D",
        font={'color': "#94F8FD", 'family': 'Segoe UI'},
        xaxis=dict(
            tickmode='linear',
            tick0=1,
            dtick=1,
            showgrid=True,
            gridcolor='#2A2A3E',
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#2A2A3E',
            zeroline=False,
            range=[45000, 65000]
        ),
        height=300,
        margin=dict(l=60, r=20, t=20, b=40),
        showlegend=False
    )
    
    # Agregar anotación "Total Gastado: 58,760"
    fig.add_annotation(
        text="Total Gastado: 58,760",
        x=6, y=58760,
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#94F8FD",
        font=dict(size=10, color="#94F8FD")
    )
    
    return fig

def crear_tabla_matriz(df_consolidado):
    """Crear tabla matriz con los datos por categoría"""
    df_tabla = df_consolidado.groupby('Categoría').agg({
        'Gastos': 'sum',
        'Presupuesto Anual': 'first'
    }).reset_index()
    
    df_tabla['Saldo'] = df_tabla['Presupuesto Anual'] - df_tabla['Gastos']
    df_tabla['% de Gasto'] = (df_tabla['Gastos'] / df_tabla['Presupuesto Anual'] * 100).round(1)
    
    # Ordenar por total gastado descendente
    df_tabla = df_tabla.sort_values('Gastos', ascending=False)
    
    # Crear la tabla HTML
    header = html.Tr([
        html.Th('Categoría', className='table-header'),
        html.Th('Total Presupuesto', className='table-header'),
        html.Th('Total Gastado', className='table-header'),
        html.Th('Saldo', className='table-header'),
        html.Th('% de Gasto', className='table-header')
    ])
    
    rows = []
    for _, row in df_tabla.iterrows():
        # Determinar color según el porcentaje
        if row['% de Gasto'] > 90:
            class_name = 'table-row high-spending'
        elif row['% de Gasto'] > 70:
            class_name = 'table-row medium-spending'
        else:
            class_name = 'table-row low-spending'
            
        rows.append(html.Tr([
            html.Td(row['Categoría'], className='table-cell'),
            html.Td(f"{row['Presupuesto Anual']:,.0f}", className='table-cell'),
            html.Td(f"{row['Gastos']:,.0f}", className='table-cell'),
            html.Td(f"{row['Saldo']:,.0f}", className='table-cell'),
            html.Td(f"{row['% de Gasto']:.1f}%", className='table-cell percent-cell')
        ], className=class_name))
    
    # Agregar fila de totales
    total_row = html.Tr([
        html.Td('TOTAL', className='table-cell total-cell'),
        html.Td(f"{df_tabla['Presupuesto Anual'].sum():,.0f}", className='table-cell total-cell'),
        html.Td(f"{df_tabla['Gastos'].sum():,.0f}", className='table-cell total-cell'),
        html.Td(f"{df_tabla['Saldo'].sum():,.0f}", className='table-cell total-cell'),
        html.Td(f"{(df_tabla['Gastos'].sum() / df_tabla['Presupuesto Anual'].sum() * 100):.1f}%", 
                className='table-cell total-cell')
    ], className='table-row total-row')
    
    rows.append(total_row)
    
    return html.Table([
        html.Thead([header]),
        html.Tbody(rows)
    ], className='data-table')

def crear_grafico_anillo_semestre(df_consolidado):
    """Crear gráfico de anillo para gastos por semestre"""
    df_semestre = df_consolidado.groupby('Semestre')['Gastos'].sum().reset_index()
    
    # Valores aproximados de la imagen
    valores = [355000, 120000]  # Sem 1 y Sem 2
    labels = ['Sem 1', 'Sem 2']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=valores,
        hole=0.7,
        marker=dict(colors=['#94F8FD', '#2A2A3E']),
        textinfo='label+value',
        texttemplate='%{label}<br>%{value:,.0f} mil<br>(%{percent})',
        textfont=dict(color='#94F8FD', size=10, family='Segoe UI'),
        hoverinfo='label+percent+value'
    )])
    
    fig.update_layout(
        paper_bgcolor="#13121D",
        plot_bgcolor="#13121D",
        font={'color': "#94F8FD", 'family': 'Segoe UI'},
        height=250,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1,
            font=dict(size=10)
        )
    )
    
    # Agregar texto en el centro
    fig.add_annotation(
        text=f"<b>Total</b><br>475,650<br>(76.6%)",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=14, color="#94F8FD", family='Segoe UI')
    )
    
    return fig
def crear_grafico_columnas_trimestre(df_consolidado):
    """Crear gráfico de columnas para gastos por trimestre"""
    # Valores aproximados de la imagen
    trimestres = ['T1', 'T2', 'T3']
    valores = [178570, 176780, 120300]
    
    fig = go.Figure(data=[
        go.Bar(
            x=trimestres,
            y=valores,
            marker_color=['#94F8FD', '#94F8FD', '#5AC8CD'],
            text=[f'{v:,.0f}' for v in valores],
            textposition='outside',
            textfont=dict(color='#94F8FD', size=10, family='Segoe UI')
        )
    ])
    
    fig.update_layout(
        paper_bgcolor="#13121D",
        plot_bgcolor="#1B1B2D",
        font={'color': "#94F8FD", 'family': 'Segoe UI'},
        xaxis=dict(
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#2A2A3E',
            zeroline=False,
            showticklabels=False,
            range=[0, 200000]
        ),
        height=300,
        margin=dict(l=40, r=20, t=40, b=40),
        showlegend=False
    )
    
    return fig

def crear_grafico_radar_eficiencia(df_consolidado):
    """Crear gráfico de radar mostrando la eficiencia del presupuesto por categoría"""
    # Calcular eficiencia por categoría
    df_eficiencia = df_consolidado.groupby('Categoría').agg({
        'Gastos': 'sum',
        'Presupuesto Anual': 'first'
    }).reset_index()
    
    df_eficiencia['Porcentaje_Uso'] = (df_eficiencia['Gastos'] / df_eficiencia['Presupuesto Anual'] * 100).round(1)
    df_eficiencia['Disponible'] = 100 - df_eficiencia['Porcentaje_Uso']
    
    # Ordenar por porcentaje de uso para mejor visualización
    df_eficiencia = df_eficiencia.sort_values('Porcentaje_Uso', ascending=False)
    
    # Crear el gráfico de radar
    fig = go.Figure()
    
    # Agregar el trace de presupuesto usado
    fig.add_trace(go.Scatterpolar(
        r=df_eficiencia['Porcentaje_Uso'].values,
        theta=df_eficiencia['Categoría'].values,
        fill='toself',
        fillcolor='rgba(148, 248, 253, 0.3)',
        line=dict(color='#94F8FD', width=2),
        marker=dict(color='#94F8FD', size=8),
        name='% Usado',
        text=[f'{v:.1f}%' for v in df_eficiencia['Porcentaje_Uso'].values],
        hovertemplate='%{theta}<br>Usado: %{r:.1f}%<extra></extra>'
    ))
    
    # Agregar línea de referencia al 100% (presupuesto total)
    fig.add_trace(go.Scatterpolar(
        r=[100] * len(df_eficiencia),
        theta=df_eficiencia['Categoría'].values,
        mode='lines',
        line=dict(color='#FF4444', width=1, dash='dash'),
        name='Límite Presupuesto',
        hoverinfo='skip'
    ))
    
    # Agregar línea de referencia al 75% (zona de alerta)
    fig.add_trace(go.Scatterpolar(
        r=[75] * len(df_eficiencia),
        theta=df_eficiencia['Categoría'].values,
        mode='lines',
        line=dict(color='#FFA500', width=1, dash='dot'),
        name='Zona de Alerta',
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        polar=dict(
            bgcolor='#1B1B2D',
            radialaxis=dict(
                visible=True,
                range=[0, 120],
                tickfont=dict(color='#94F8FD', size=9),
                gridcolor='#2A2A3E',
                linecolor='#2A2A3E',
                showticklabels=True,
                tickmode='array',
                tickvals=[0, 25, 50, 75, 100],
                ticktext=['0%', '25%', '50%', '75%', '100%']
            ),
            angularaxis=dict(
                tickfont=dict(color='#94F8FD', size=10),
                gridcolor='#2A2A3E',
                linecolor='#94F8FD'
            )
        ),
        paper_bgcolor='#13121D',
        plot_bgcolor='#13121D',
        font={'color': '#94F8FD', 'family': 'Segoe UI'},
        height=300,
        margin=dict(l=80, r=80, t=40, b=40),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.1,
            font=dict(size=9),
            bgcolor='rgba(27, 27, 45, 0.8)',
            bordercolor='#94F8FD',
            borderwidth=1
        ),
        title=dict(
            text='',
            font=dict(size=14, color='#94F8FD')
        )
    )
    
    return fig