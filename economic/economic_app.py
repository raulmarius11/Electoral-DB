import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import geopandas as gpd
from sqlalchemy import create_engine, text
from django_plotly_dash import DjangoDash  # Import DjangoDash instead of Dash
import os
import sys
import django

# Ensure the path to the Django project is added
path_to_project = 'C:/Users/Raul/Desktop/Django-project'
if path_to_project not in sys.path:
    sys.path.append(path_to_project)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'databaseproject.settings')
django.setup()

# Connect to the PostgreSQL database
engine = create_engine('postgresql+psycopg2://postgres:electo123@localhost:5432/sp_project_utf8')

# Initialize DjangoDash app
app = DjangoDash('economic') 

# App layout
app.layout = html.Div([
    html.Link(rel='stylesheet', href='/static/css/styles.css'),  # Link to external CSS

    html.Div(id='title-container', style={'textAlign': 'center', 'fontSize': 24, 'marginTop': '10px', 'marginBottom': '20px'}),
    
    html.Div([
        # Left side: Checklist and options
        html.Div([
            dcc.Checklist(
                id='graph-type-checklist',
                options=[
                    {'label': 'Map', 'value': 'map'},
                    {'label': 'Time Series', 'value': 'time_series'},
                    {'label': 'Bar Chart (Top 10)', 'value': 'bar_chart'}
                ],
                value=['map'],  # Default to 'map'
                labelStyle={'display': 'block', 'margin-bottom': '10px', 'color': 'blue'}
            ),
            dcc.Dropdown(
                id='variable-dropdown',
                options=[{'label': i, 'value': i} for i in sorted(pd.read_sql('SELECT DISTINCT "variable_name" FROM economic', engine)['variable_name'])],
                placeholder="Select a variable",
                className='dash-dropdown',
                style={'width': '100%', 'margin-bottom': '20px', 'fontSize': 12}
            ),
            dcc.Dropdown(
                id='year-dropdown',
                placeholder="Select a year",
                className='dash-dropdown',
                style={'width': '100%', 'margin-bottom': '20px', 'fontSize': 12}
            ),
            dcc.Dropdown(
                id='county-dropdown',
                options=[{'label': i, 'value': i} for i in pd.read_sql('SELECT "nume" FROM localitati WHERE "Tip" = \'Judeţ\'', engine)['nume']],
                placeholder="Select a county for the time series",
                className='dash-dropdown',
                style={'width': '100%', 'margin-bottom': '20px', 'fontSize': 12}
            ),
            html.P("*County selection applies only to the Time Series graph", style={'color': 'gray', 'fontSize': 12}),
        ], style={'width': '20%', 'display': 'inline-block', 'verticalAlign': 'top'}),  # Left side, 20% width

        # Right side: Graphs (Map + Time Series & Bar Chart in one line)
        html.Div([
            html.Div([
                dcc.Loading(
                    id='loading-map',
                    type='default',
                    children=[
                        # Left: Map
                        dcc.Graph(id='economic-map', style={'width': '49%', 'display': 'inline-block', 'height': '600px'}),
                        
                        # Right: Time Series and Bar Chart (stacked vertically)
                        html.Div([
                            dcc.Graph(id='time-series-graph', style={'width': '100%', 'height': '300px'}),
                            dcc.Graph(id='bar-chart-graph', style={'width': '100%', 'height': '300px'}),
                        ], style={'width': '49%', 'display': 'inline-block', 'verticalAlign': 'top'})
                    ],
                    style={'textAlign': 'center', 'fontSize': 20}
                )
            ], style={'display': 'inline-block', 'width': '100%'})
        ], style={'display': 'inline-block', 'width': '80%'})  # Right side, 80% width
    ], style={'display': 'inline-block', 'width': '100%'})
])


# Callback to update the year dropdown based on the selected variable
@app.callback(
    Output('year-dropdown', 'options'),
    [Input('variable-dropdown', 'value')]
)
def update_year_dropdown(selected_variable):
    if selected_variable:
        df_years = pd.read_sql(f'SELECT DISTINCT "year" FROM economic WHERE "variable_name" = \'{selected_variable}\' ORDER BY "year"', engine)
        year_options = [{'label': 'All Years', 'value': 'all_years'}] + [{'label': str(year), 'value': year} for year in df_years['year']]
        return year_options
    return []

# Callback to update the graphs based on variable, year, selected graph types, and county
@app.callback(
    [Output('economic-map', 'figure'),
     Output('time-series-graph', 'figure'),
     Output('bar-chart-graph', 'figure')],
    [Input('graph-type-checklist', 'value'),
     Input('variable-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('county-dropdown', 'value')]
)
def update_graph(graph_types, variable, year, county):
    # Placeholder for no data
    empty_graph = {
        'data': [],
        'layout': {
            'xaxis': {'visible': False},
            'yaxis': {'visible': False},
            'annotations': [{
                'text': "Please select a variable and a year to display the graphs.",
                'xref': "paper",
                'yref': "paper",
                'showarrow': False,
                'font': {'size': 20}
            }]
        }
    }
    
    if not variable or not year:
        return empty_graph, empty_graph, empty_graph

    # Build SQL query for the Map and Bar Chart
    query = f"""
    SELECT SUM(E."value") as value, L."geometrie", L."Judet", L."Siruta", L."nume" as county_name
    FROM economic E
    JOIN localitati L ON E."siruta" = L."Siruta"
    WHERE E."variable_name" = '{variable}'
    """
    
    # Filter by selected year or sum all years
    if year != 'all_years':
        query += f' AND E."year" = {year}'
    
    query += " GROUP BY L." + '"Siruta", L."geometrie", L."Judet", L."nume"'
    
    # Fetch data for the Map and Bar Chart
    with engine.connect() as conn:
        df_result = gpd.read_postgis(query, conn, geom_col='geometrie')

    if df_result.empty:
        return empty_graph, empty_graph, empty_graph
    
    df_result['value_million'] = df_result['value'] / 1_000_000  # Format values in millions
    df_result['log_value'] = np.log1p(df_result['value_million'])  # Logarithmic scale to compress large outliers
    
    # Initialize empty figures
    map_fig = empty_graph
    time_series_fig = empty_graph
    bar_chart_fig = empty_graph
    
    # Map Figure
    if 'map' in graph_types:
        map_fig = px.choropleth_mapbox(df_result, geojson=df_result.geometry.__geo_interface__,
                                       locations=df_result.index,
                                       color="log_value",
                                       mapbox_style="white-bg",
                                       color_continuous_scale=['red', 'yellow', 'green'],
                                       center={"lat": 45.9432, "lon": 24.9668},
                                       zoom=5,
                                       opacity=0.5,
                                       hover_data={"county_name": True, "value_million": ":.2f"})

        # Custom hover template for map
        map_fig.update_traces(
            hovertemplate="<b>%{customdata[0]}</b><br>Sum in RON (millions): %{customdata[1]:.2f} million"
        )
        map_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, coloraxis_showscale=False)

    # Bar Chart (Top 10) Figure
    if 'bar_chart' in graph_types:
        df_result = df_result.sort_values(by='value', ascending=False).head(10)
        bar_chart_fig = px.bar(df_result, x='county_name', y='value_million', text='value_million',
                               title="Top 10 Counties by Value", labels={'value_million': 'Value (Millions RON)'})
        
        # Add annotation about the top 10
        bar_chart_fig.update_layout(
            annotations=[{
                'text': 'Only Top 10 shown',
                'x': 0.5,
                'y': -0.15,
                'xref': 'paper',
                'yref': 'paper',
                'showarrow': False,
                'font': {'size': 12, 'color': 'gray'}
            }]
        )
        bar_chart_fig.update_layout(margin={"r": 0, "t": 40, "l": 40, "b": 40})

    # Time Series Figure
    if 'time_series' in graph_types and county:
        time_series_query = f"""
        SELECT SUM(E."value") as value, E."year"
        FROM economic E
        JOIN localitati L ON E."siruta" = L."Siruta"
        WHERE L."nume" = '{county}' AND E."variable_name" = '{variable}'
        GROUP BY E."year"
        ORDER BY E."year"
        """
        
        df_time_series = pd.read_sql(time_series_query, engine)
        
        # Create time series chart
        time_series_fig = px.line(df_time_series, x='year', y='value', title=f"Time Series for {county}",
                                  labels={'value': 'Value (RON)'})
        time_series_fig.update_traces(hovertemplate='Year: %{x}<br>Value: %{y:.2f} RON')

    return map_fig, time_series_fig, bar_chart_fig

# This code will run in a Django environment where you can include it in your web application.
