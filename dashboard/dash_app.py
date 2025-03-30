import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine, text
from django_plotly_dash import DjangoDash  # Import DjangoDash instead of Dash
import os
import sys
import django

# Asigură-te că adaugi calea către directorul care conține `databaseproject`
path_to_project = 'C:/Users/Raul/Desktop/Django-project'
if path_to_project not in sys.path:
    sys.path.append(path_to_project)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'databaseproject.settings')
django.setup()

# Conectează-te la baza de date PostgreSQL
engine = create_engine('postgresql+psycopg2://postgres:electo123@localhost:5432/sp_project_utf8')

# Inițializează aplicația DjangoDash în loc de Dash
app = DjangoDash('dashboard_app')  # The name 'dashboard_app' can be anything

# Layout-ul aplicației
app.layout = html.Div([
    html.Link(rel='stylesheet', href='/static/css/styles.css'),

    html.Div(id='title-container', style={'textAlign': 'center', 'fontSize': 24, 'marginTop': '10px', 'marginBottom': '20px'}),

    html.Div([
        html.Div([
            dcc.Dropdown(
                id='alegeri-dropdown',
                options=[{'label': i, 'value': i} for i in pd.read_sql('SELECT DISTINCT "tip" FROM Alegeri', engine)['tip']],
                placeholder="Select election type.",
                className='dash-dropdown',
                style={'width': '100%', 'margin-bottom': '20px', 'fontSize': 12}
            ),
            dcc.Dropdown(
                id='an-dropdown',
                placeholder="Select year.",
                className='dash-dropdown',
                style={'width': '100%', 'margin-bottom': '20px', 'fontSize': 12}
            ),
            dcc.Dropdown(
                id='tur-dropdown',
                placeholder="Select election round.",
                className='dash-dropdown',
                style={'width': '100%', 'margin-bottom': '20px', 'fontSize': 12}
            ),
            dcc.Dropdown(
                id='candidat-dropdown',
                placeholder="Select candidate.",
                className='dash-dropdown',
                style={'width': '100%', 'margin-bottom': '20px', 'fontSize': 12}
            ),
            dcc.Dropdown(
                id='zona-dropdown',
                options=[{'label': 'Toate Judetele', 'value': 'all'}] + 
                        sorted([{'label': i, 'value': i} for i in pd.read_sql('SELECT DISTINCT "Judet" FROM Localitati ORDER BY "Judet"', engine)['Judet']], key=lambda x: x['label']),
                placeholder="Select county:",
                className='dash-dropdown',
                style={'width': '100%', 'margin-bottom': '20px', 'fontSize': 12}
            ),
            dcc.Checklist(
                id='display-options',
                options=[
                    {'label': 'Hartă', 'value': 'harta'},
                    {'label': 'Pie Chart', 'value': 'pie-chart'},
                    {'label': 'Bar Chart', 'value': 'bar-chart'}  # Adăugat Bar Chart ca opțiune
                ],
                value=['harta'],
                labelStyle={'display': 'block', 'margin-bottom': '10px', 'color': 'blue'}
            ),
        ], style={'width': '15%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        html.Div([
            dcc.Graph(id='harta', style={'width': '100%', 'height': '600px'}),
            dcc.Graph(id='pie-chart', style={'width': '100%', 'height': '600px'}),
            dcc.Graph(id='bar-chart', style={'width': '100%', 'height': '600px'})  # Adăugat Bar Chart
        ], style={'width': '83%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding-left': '2%'})
    ], style={'display': 'inline-block', 'width': '100%'})
])

# Callback pentru actualizarea titlului și gestionarea afișării graficelor
@app.callback(
    [Output('title-container', 'children'),
     Output('harta', 'style'),
     Output('pie-chart', 'style'),
     Output('bar-chart', 'style')],  # Adăugat bar-chart
    [Input('display-options', 'value'),
     Input('zona-dropdown', 'value')]
)
def update_title_and_display(selected_charts, zona):
    # Actualizarea titlului în funcție de zona selectată
    title = 'Romania' if zona == 'all' or not zona else zona
    
    # Gestionarea afișării graficelor
    harta_style = {'display': 'inline-block', 'width': '50%'} if 'harta' in selected_charts else {'display': 'none'}
    pie_chart_style = {'display': 'inline-block', 'width': '25%'} if 'pie-chart' in selected_charts else {'display': 'none'}
    bar_chart_style = {'display': 'inline-block', 'width': '25%'} if 'bar-chart' in selected_charts else {'display': 'none'}  # Stil pentru bar-chart
    
    # Dacă doar unul este selectat, ocupă toată lățimea
    if len(selected_charts) == 1:
        if 'harta' in selected_charts:
            harta_style['width'] = '100%'
        if 'pie-chart' in selected_charts:
            pie_chart_style['width'] = '100%'
        if 'bar-chart' in selected_charts:  # Adăugat condiție pentru bar-chart
            bar_chart_style['width'] = '100%'
    
    return title, harta_style, pie_chart_style, bar_chart_style

# Callback pentru popularea dropdown-ului "an" în funcție de "tip_alegere"
@app.callback(
    Output('an-dropdown', 'options'),
    [Input('alegeri-dropdown', 'value')]
)
def set_an_options(tip_alegere):
    if tip_alegere:
        query = f'SELECT DISTINCT "an" FROM Alegeri WHERE "tip" = \'{tip_alegere}\' ORDER BY "an"'
        with engine.connect() as conn:
            result = conn.execute(text(query))
            options = [{'label': str(row[0]), 'value': row[0]} for row in result]
        return options
    return []

# Callback pentru popularea dropdown-ului "tur" în funcție de "tip_alegere" și "an"
@app.callback(
    Output('tur-dropdown', 'options'),
    [Input('alegeri-dropdown', 'value'), Input('an-dropdown', 'value')]
)
def set_tur_options(tip_alegere, an):
    if tip_alegere and an:
        query = f'SELECT DISTINCT "tur" FROM Alegeri WHERE "tip" = \'{tip_alegere}\' AND "an" = {an} ORDER BY "tur"'
        with engine.connect() as conn:
            result = conn.execute(text(query))
            options = [{'label': row[0], 'value': row[0]} for row in result]
        return options
    return []

# Callback pentru popularea dropdown-ului "candidat" în funcție de "tip_alegere", "an", și "tur"
@app.callback(
    Output('candidat-dropdown', 'options'),
    [Input('alegeri-dropdown', 'value'), Input('an-dropdown', 'value'), Input('tur-dropdown', 'value')]
)
def set_candidat_options(tip_alegere, an, tur):
    if tip_alegere and an and tur:
        query = f"""
        SELECT DISTINCT C."nume_candidat" 
        FROM Alegeri A
        JOIN Candidati C ON A.id_candidat = C.id_candidat 
        WHERE A."tip" = '{tip_alegere}' AND A."an" = {an} AND A."tur" = '{tur}'
        """
        with engine.connect() as conn:
            result = conn.execute(text(query))
            options = [{'label': row[0], 'value': row[0]} for row in result]
        return options
    return []

# Callback pentru actualizarea hărții și a graficului pie în funcție de selecțiile făcute
@app.callback(
    [Output('harta', 'figure'),
     Output('pie-chart', 'figure'),
     Output('bar-chart', 'figure')],  # Adăugat bar-chart
    [Input('alegeri-dropdown', 'value'),
     Input('an-dropdown', 'value'),
     Input('tur-dropdown', 'value'),
     Input('candidat-dropdown', 'value'),
     Input('zona-dropdown', 'value')]
)
def update_harta(tip_alegere, an, tur, candidat, zona):
    # Verifică dacă toate valorile necesare sunt disponibile
    if not all([tip_alegere, an, tur, candidat]):
        return {
            "layout": {
                "xaxis": {"visible": False},
                "yaxis": {"visible": False},
                "annotations": [{
                    "text": "Select all variables please.",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 20}
                }]
            }
        }, {}, {}  # Adăugat {} pentru bar-chart

    # Construiește interogarea SQL pe baza selecțiilor făcute
    query = f"""
    SELECT A."numar_voturi", A."voturi_procentuale", L.geometrie, L."Judet", L."nume" AS "nume_localitate", C."culoare", C."nume_candidat"
    FROM Alegeri A 
    JOIN Localitati L ON A."Siruta" = L."Siruta" 
    JOIN Candidati C ON A.id_candidat = C.id_candidat 
    WHERE A."tip" = '{tip_alegere}' 
    AND A."an" = {an} 
    AND A."tur" = '{tur}' 
    AND C."nume_candidat" = '{candidat}'
    """

    # Filtrează după zona selectată (judet) sau toate judetele
    if zona and zona != 'all':
        query += f' AND L."Judet" = \'{zona}\''
    else:
        query += ' AND L."Tip" = \'Judeţ\''  # Asigură-te că se filtrează doar județele

    # Rularea interogării SQL și extragerea rezultatelor
    with engine.connect() as conn:
        df_result = gpd.read_postgis(query, conn, geom_col='geometrie')

    # Setarea centrului și zoom-ului pentru harta în funcție de selecție


    if zona and zona != 'all':
        # Obține centrul geometriei județului selectat
        geometry = df_result['geometrie'].unary_union
        centroid = geometry.centroid
        center = {"lat": centroid.y, "lon": centroid.x}
        zoom = 7.5  # Zoom ridicat pentru vizualizarea unui județ
    else:
        center = {"lat": 45.9432, "lon": 24.9668}
        zoom = 5  # Zoom pentru întreaga Românie
    cy = ['#FFFFE0', '#FFFACD', '#FAFAD2', '#FFEFD5', '#FFD700', '#FFEB3B', '#FDD835']

    # Extrage numele paletei de culori din rezultatul SQL
    color_palette = df_result['culoare'].iloc[0]
    if color_palette == 'cy':
        fig = px.choropleth_mapbox(df_result, geojson=df_result.geometry, 
                                locations=df_result.index, 
                                color="voturi_procentuale",
                                color_continuous_scale=cy,  # Paleta personalizată
                                mapbox_style="white-bg", 
                                center=center,
                                zoom=zoom,
                                opacity=0.5)
    else:
        # Crearea hărții cu Plotly, folosind culoarea din baza de date și adăugând voturile procentuale normalizate
        fig = px.choropleth_mapbox(df_result, geojson=df_result.geometry, 
                                locations=df_result.index, 
                                color="voturi_procentuale",
                                color_continuous_scale=color_palette,  # Folosește paleta de culori
                                mapbox_style="white-bg",  # Stil fără fundal
                                center=center,
                                zoom=zoom,
                                opacity=0.5)  # Setează opacitatea pentru a vedea doar zonele colorate
    
    # Elimină legenda de pe hartă
    fig.update_layout(showlegend=False)
    fig.update_layout(coloraxis_showscale=False)

    # Adaugă voturile totale, procentuale, numele localității și al județului pe hover
    fig.update_traces(
        hovertemplate='<b>%{customdata[1]} - %{customdata[2]}</b><br>Voturi Totale: %{customdata[0]}<br>Procentaj: %{z:.2f}%<extra></extra>',
        customdata=df_result[['numar_voturi', 'nume_localitate', 'Judet']]
    )

        # Construirea Pie Chart-ului și a Bar Chart-ului
    query_pie = f"""
    SELECT C."nume_candidat", SUM(A."numar_voturi") as total_voturi, C."culoare", 
        SUM(A."voturi_procentuale") as procente, C."tip_candidat", C."abreviere"
    FROM Alegeri A 
    JOIN Candidati C ON A.id_candidat = C.id_candidat 
    JOIN Localitati L ON A."Siruta" = L."Siruta" 
    WHERE A."tip" = '{tip_alegere}' 
    AND A."an" = {an} 
    AND A."tur" = '{tur}'
    """

    if zona and zona != 'all':
        query_pie += f' AND L."Judet" = \'{zona}\''

    query_pie += " GROUP BY C.nume_candidat, C.culoare, C.tip_candidat, C.abreviere"

    with engine.connect() as conn:
        df_pie = pd.read_sql(query_pie, conn)

    # Calcularea procentului corect pentru fiecare candidat din totalul general
    total_voturi_general = df_pie['total_voturi'].sum()
    df_pie['procente'] = df_pie['total_voturi'] / total_voturi_general * 100

    # Adăugarea unei coloane pentru afișarea corectă a numelor în funcție de tipul candidatului
    df_pie['nume_afisat'] = df_pie.apply(lambda row: row['abreviere'] if row['tip_candidat'] == 'partid' else row['nume_candidat'], axis=1)

    # Ordonare după procente în ordine descrescătoare
    df_pie = df_pie.sort_values(by='procente', ascending=False)

    # Definirea mapping-ului de culori (dacă nu este definit deja)
    color_mapping = {
        "Mircea Diaconu": "purple",
        "Ilie-Dan Barna": "blue",
        "Hunor Kelemen": "green",
        "PARTIDUL ROMÂNIA MARE": "purple",
        "PARTIDUL NAȚIONAL LIBERAL": "yellow",
        "PARTIDUL SOCIAL DEMOCRAT": "red",
        "Alexandru Cumpănașu": "pink",
        "Theodor Paleologu": "orange",
        "PARTIDUL MIȘCAREA POPULARĂ": "orange",
        "Ramona-Ioana Bruynseels": "gray",
        "PARTIDUL ROMÂNIA UNITĂ": "brown",
        "Klaus-Werner Iohannis": "yellow",
        "UNIUNEA SALVAȚI ROMÂNIA": "blue",
        "PARTIDUL ALIANȚA LIBERALILOR ȘI DEMOCRAȚILOR": "darkblue",
        "Vasilica-Viorica Dancilă": "red",
        "UNIUNEA DEMOCRATĂ MAGHIARĂ DIN ROMÂNIA": "green"
    }

    # Crearea Pie Chart-ului
    pie_chart = px.pie(df_pie, names='nume_candidat', values='procente', color='nume_candidat',
                    color_discrete_map=color_mapping)

    pie_chart.update_traces(textinfo='percent', hoverinfo='label+percent+value')

    pie_chart.update_layout(showlegend=False)

    # Crearea Bar Chart-ului, folosind numele afișat (abreviere pentru partide și nume candidat pentru restul)
    bar_chart = px.bar(df_pie, x='nume_afisat', y='procente', color='nume_candidat',
                    color_discrete_map=color_mapping, text='procente')

    bar_chart.update_traces(texttemplate='%{text:.2f}%', textposition='outside')

    bar_chart.update_layout(showlegend=False)

    return fig, pie_chart, bar_chart
