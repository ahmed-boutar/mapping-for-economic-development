# import dash
# from dash import dcc, html
# from dash.dependencies import Input, Output
# import plotly.graph_objects as go
# import geopandas as gpd
# import h3
# import pandas as pd

# app = dash.Dash(__name__)

# # Load and process data outside of the callback
# def load_population_density():
#     gdf = gpd.read_file('../../data/kontur_population_KE_20231101.gpkg')
#     gdf_wgs84 = gdf.to_crs(epsg=4326)
#     gdf['lon'] = gdf_wgs84.geometry.centroid.x
#     gdf['lat'] = gdf_wgs84.geometry.centroid.y
#     gdf['lat'] = gdf['lat'].astype('float32')
#     gdf['lon'] = gdf['lon'].astype('float32')
#     return gdf

# def create_multi_resolution_data(df, min_resolution, max_resolution):
#     multi_res_list = []
    
#     for res in range(min_resolution, max_resolution + 1):
#         df_res = df.copy()
#         df_res['h3_parent'] = df_res['h3'].apply(lambda x: h3.h3_to_parent(x, res))
#         df_res = df_res.groupby('h3_parent').agg({
#             'population': 'sum',
#             'lat': 'mean',
#             'lon': 'mean'
#         }).reset_index()
#         df_res['resolution'] = res
#         multi_res_list.append(df_res)
    
#     return pd.concat(multi_res_list, ignore_index=True)

# # Convert H3 hexagons to polygon coordinates for plotting
# def h3_to_polygon_coordinates(h3_index):
#     boundary = h3.h3_to_geo_boundary(h3_index, geo_json=True)
#     lons, lats = zip(*boundary)
#     return list(lons), list(lats)

# # Load data once when the app starts
# gdf = load_population_density()
# gdf['h3'] = gdf.apply(lambda row: h3.geo_to_h3(row['lat'], row['lon'], 8), axis=1)
# population_df_all_res = create_multi_resolution_data(gdf, min_resolution=3, max_resolution=8)

# app.layout = html.Div([
#     dcc.Graph(id='hexagon-map', style={'height': '90vh'}),
# ])

# @app.callback(
#     Output('hexagon-map', 'figure'),
#     Input('hexagon-map', 'relayoutData')
# )
# def update_map(relayoutData):
#     if relayoutData is None:
#         zoom = 3
#     else:
#         zoom = relayoutData.get('mapbox.zoom', 3)
    
#     # Determine which resolution to use based on zoom level
#     resolution = min(max(int(zoom), 3), 8)
    
#     df_to_plot = population_df_all_res[population_df_all_res['resolution'] == resolution]
    
#     fig = go.Figure()

#     # Plot each hexagon as a filled polygon
#     for _, row in df_to_plot.iterrows():
#         hex_lon, hex_lat = h3_to_polygon_coordinates(row['h3_parent'])
#         fig.add_trace(go.Scattermapbox(
#             fill="toself",
#             lon=hex_lon,
#             lat=hex_lat,
#             mode='lines',
#             fillcolor='rgba(0, 150, 0, 0.5)',
#             line=dict(width=1),
#             hoverinfo='text',
#             text=f"Population: {row['population']}",
#             showlegend=False,
#         ))

#     fig.update_layout(
#         mapbox_style="carto-positron",
#         mapbox=dict(
#             center=dict(lat=-1.286389, lon=36.817223),
#             zoom=zoom,
#             style='carto-positron'
#         ),
#         margin={"r":0,"t":0,"l":0,"b":0},
#     )

#     return fig

# if __name__ == '__main__':
#     app.run_server(debug=True)


# import dash
# from dash import dcc, html
# from dash.dependencies import Input, Output
# import plotly.graph_objects as go
# import geopandas as gpd
# import h3
# import pandas as pd
# import numpy as np
# from functools import lru_cache
# from shapely.geometry import Polygon
# import json

# app = dash.Dash(__name__)

# def load_population_density():
#     gdf = gpd.read_file('../../data/kontur_population_KE_20231101.gpkg')
#     gdf_wgs84 = gdf.to_crs(epsg=4326)
#     gdf['lon'] = gdf_wgs84.geometry.centroid.x
#     gdf['lat'] = gdf_wgs84.geometry.centroid.y
#     gdf['lat'] = gdf['lat'].astype('float32')
#     gdf['lon'] = gdf['lon'].astype('float32')
#     return gdf

# @lru_cache(maxsize=1024)
# def h3_to_polygon_coordinates(h3_index):
#     """Cache polygon coordinate calculations"""
#     boundary = h3.h3_to_geo_boundary(h3_index, geo_json=True)
#     lons, lats = zip(*boundary)
#     return list(lons), list(lats)

# class HexagonDataManager:
#     def __init__(self, df, min_resolution, max_resolution):
#         self.hex_data = {}
#         self.min_resolution = min_resolution
#         self.max_resolution = max_resolution
#         self._precompute_data(df)
        
#     def _precompute_data(self, df):
#         print("Precomputing hexagon data...")
#         for res in range(self.min_resolution, self.max_resolution + 1):
#             print(f"Processing resolution {res}...")
#             self.hex_data[res] = {}
#             df_res = df.copy()
#             df_res['h3_parent'] = df_res['h3'].apply(lambda x: h3.h3_to_parent(x, res))
            
#             grouped = df_res.groupby('h3_parent').agg({
#                 'population': 'sum',
#                 'lat': 'mean',
#                 'lon': 'mean'
#             }).reset_index()
            
#             for _, row in grouped.iterrows():
#                 h3_idx = row['h3_parent']
#                 lons, lats = h3_to_polygon_coordinates(h3_idx)
                
#                 self.hex_data[res][h3_idx] = {
#                     'population': float(row['population']),  # Convert to float for JSON serialization
#                     'coordinates': (lons, lats),
#                     'center': (float(row['lon']), float(row['lat']))  # Convert to float for JSON serialization
#                 }
#         print("Precomputation complete!")

#     def get_visible_hexagons(self, bounds, resolution):
#         """Filter hexagons based on viewport bounds"""
#         min_lon, min_lat, max_lon, max_lat = bounds
        
#         # Create a polygon from the viewport bounds
#         viewport_polygon = Polygon([
#             [min_lon, min_lat],
#             [max_lon, min_lat],
#             [max_lon, max_lat],
#             [min_lon, max_lat],
#             [min_lon, min_lat]
#         ])
        
#         # Get the coordinates of the viewport polygon
#         viewport_coords = [[lat, lon] for lon, lat in viewport_polygon.exterior.coords[:-1]]
        
#         # Use H3's polyfill to get hexagons that intersect with the viewport
#         hexagons = h3.polyfill(
#             {"type": "Polygon", "coordinates": [viewport_coords]},
#             resolution,
#             geo_json_conformant=True
#         )
        
#         # Filter hexagons that exist in our dataset
#         visible_hexagons = []
#         for h3_idx in hexagons:
#             if h3_idx in self.hex_data[resolution]:
#                 visible_hexagons.append(
#                     (h3_idx, self.hex_data[resolution][h3_idx])
#                 )
        
#         return visible_hexagons

# # Load data and initialize manager
# print("Loading data...")
# gdf = load_population_density()
# MIN_RESOLUTION = 3
# MAX_RESOLUTION = 8

# print("Initializing HexagonDataManager...")
# hex_manager = HexagonDataManager(gdf, MIN_RESOLUTION, MAX_RESOLUTION)

# # Calculate population range for color scaling
# all_populations = []
# for res in hex_manager.hex_data:
#     populations = [data['population'] for data in hex_manager.hex_data[res].values()]
#     all_populations.extend(populations)
# pop_min, pop_max = np.percentile(all_populations, [1, 99])

# app.layout = html.Div([
#     dcc.Graph(id='hexagon-map', style={'height': '90vh'}),
#     html.Div(id='debug-info', style={'display': 'none'})  # For debugging
# ])

# @app.callback(
#     Output('hexagon-map', 'figure'),
#     Input('hexagon-map', 'relayoutData')
# )
# def update_map(relayoutData):
#     if relayoutData is None:
#         zoom = 3
#         bounds = [-180, -90, 180, 90]  # Full world view
#     else:
#         zoom = relayoutData.get('mapbox.zoom', 3)
#         # Extract viewport bounds, falling back to full view if not available
#         if 'mapbox.bounds' in relayoutData:
#             bounds = [
#                 relayoutData['mapbox.bounds[0]'],
#                 relayoutData['mapbox.bounds[1]'],
#                 relayoutData['mapbox.bounds[2]'],
#                 relayoutData['mapbox.bounds[3]']
#             ]
#         else:
#             bounds = [-180, -90, 180, 90]
    
#     # Determine resolution based on zoom level
#     resolution = min(max(int(zoom), MIN_RESOLUTION), MAX_RESOLUTION)
    
#     # Get visible hexagons
#     visible_hexagons = hex_manager.get_visible_hexagons(bounds, resolution)
    
#     fig = go.Figure()

#     # Create traces for visible hexagons
#     for h3_idx, data in visible_hexagons:
#         lons, lats = data['coordinates']
#         population = data['population']
        
#         # Calculate color based on population
#         normalized_pop = (population - pop_min) / (pop_max - pop_min)
#         opacity = min(max(0.2 + normalized_pop * 0.6, 0.2), 0.8)
        
#         fig.add_trace(go.Scattermapbox(
#             fill="toself",
#             lon=lons,
#             lat=lats,
#             mode='lines',
#             fillcolor=f'rgba(0, 150, 0, {opacity})',
#             line=dict(width=1, color='rgba(0, 150, 0, 0.5)'),
#             hoverinfo='text',
#             text=f"Population: {int(population):,}",
#             showlegend=False,
#         ))

#     fig.update_layout(
#         mapbox_style="carto-positron",
#         mapbox=dict(
#             center=dict(lat=-1.286389, lon=36.817223),
#             zoom=zoom
#         ),
#         margin={"r":0,"t":0,"l":0,"b":0},
#     )

#     return fig

# if __name__ == '__main__':
#     print("Starting server...")
#     app.run_server(debug=True)







# import dash
# from dash import dcc, html
# from dash.dependencies import Input, Output
# import plotly.graph_objects as go
# import geopandas as gpd
# import json
# import h3
# import pandas as pd
# import numpy as np
# from shapely.geometry import Polygon, Point
# from folium import GeoJson 

# app = dash.Dash(__name__)

# def load_population_density():
#     gdf = gpd.read_file('../../data/kontur_population_KE_20231101.gpkg')
#     gdf = gdf.to_crs(epsg=4326)
#     gdf['lat'] = gdf.geometry.centroid.y
#     gdf['lon'] = gdf.geometry.centroid.x
#     return gdf

# def precompute_hexagons(df, min_res=3, max_res=8):
#     hex_json = {}
#     for res in range(min_res, max_res + 1):
#         print(f"Processing resolution {res}...")
#         df['h3'] = df.apply(lambda row: h3.geo_to_h3(row['lat'], row['lon'], res), axis=1)
        
#         grouped = df.groupby('h3').agg({
#             'population': 'sum',
#             'lat': 'mean',
#             'lon': 'mean'
#         }).reset_index()
        
#         geojson_features = []
#         for _, row in grouped.iterrows():
#             coords = h3.h3_to_geo_boundary(row['h3'], geo_json=True)
#             geojson_features.append({
#                 'type': 'Feature',
#                 'geometry': {
#                     'type': 'Polygon',
#                     'coordinates': [coords]
#                 },
#                 'properties': {
#                     'population': row['population'],
#                     'lat': row['lat'],
#                     'lon': row['lon']
#                 }
#             })
        
#         hex_json[res] = {
#             'type': 'FeatureCollection',
#             'features': geojson_features
#         }
#     print('[INFO] Processing successfully')
#     return hex_json

# # Load data and precompute hexagon GeoJSON by resolution
# gdf = load_population_density()
# hex_data = precompute_hexagons(gdf)

# app.layout = html.Div([
#     dcc.Graph(id='hexagon-map', style={'height': '90vh'}),
#     html.Div(id='debug-info', style={'display': 'none'})  # For debugging
# ])

# # app.layout = html.Div([
# #     dcc.Graph(id='hexagon-map', style={'height': '90vh'}),
# #     html.Div(id='debug-info', style={'display': 'none'})  # For debugging
# # ])

# # @app.callback(
# #     Output('hexagon-map', 'figure'),
# #     Input('hexagon-map', 'relayoutData')
# # )

# @app.callback(
#     Output('hexagon-map', 'figure'),
#     Input('hexagon-map', 'relayoutData')
# )
# def update_map(relayoutData):
#     if relayoutData is None:
#         zoom = 3
#     else:
#         zoom = relayoutData.get('mapbox.zoom', 3)
    
#     # Map zoom to resolution
#     if zoom < 5:
#         resolution = 3
#     elif zoom < 7:
#         resolution = 4
#     elif zoom < 9:
#         resolution = 5
#     else:
#         resolution = 6
    
#     # Get the hex data for the chosen resolution
#     geojson = hex_data[resolution]

#     # Set up figure
#     fig = go.Figure(go.Choroplethmapbox(
#         geojson=geojson,
#         locations=[feature["properties"]["population"] for feature in geojson["features"]],
#         z=[feature["properties"]["population"] for feature in geojson["features"]],
#         colorscale="Viridis",
#         marker_opacity=0.5,
#         marker_line_width=0
#     ))
    
#     fig.update_layout(
#         mapbox=dict(
#             style="carto-positron",
#             center=dict(lat=-1.286389, lon=36.817223),
#             zoom=zoom,
#         ),
#         margin={"r":0,"t":0,"l":0,"b":0}
#     )
    
#     return fig

# if __name__ == '__main__':
#     app.run_server(debug=True)

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import geopandas as gpd
import json
import h3
import pandas as pd
import numpy as np
from shapely.geometry import Polygon, Point
import time 

app = dash.Dash(__name__)

def load_population_density():
    gdf = gpd.read_file('../../data/kontur_population_KE_20231101.gpkg')
    gdf = gdf.to_crs(epsg=4326)
    gdf['lat'] = gdf.geometry.centroid.y
    gdf['lon'] = gdf.geometry.centroid.x
    return gdf

def precompute_hexagons(df, min_res=3, max_res=8):
    hex_json = {}
    for res in range(min_res, max_res + 1):
        print(f"Processing resolution {res}...")
        df['h3'] = df.apply(lambda row: h3.geo_to_h3(row['lat'], row['lon'], res), axis=1)
        
        grouped = df.groupby('h3').agg({
            'population': 'sum',
            'lat': 'mean',
            'lon': 'mean'
        }).reset_index()
        
        geojson_features = []
        for _, row in grouped.iterrows():
            coords = h3.h3_to_geo_boundary(row['h3'], geo_json=True)
            geojson_features.append({
                'type': 'Feature',
                'id': row['h3'],  # Assign the H3 hex code as the ID
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [coords]
                },
                'properties': {
                    'population': row['population'],
                    'lat': row['lat'],
                    'lon': row['lon']
                }
            })
        
        hex_json[res] = {
            'type': 'FeatureCollection',
            'features': geojson_features
        }
    print('[INFO] Processing successfully')
    return hex_json

# Load data and precompute hexagon GeoJSON by resolution
gdf = load_population_density()
hex_data = precompute_hexagons(gdf)

last_update_time = time.time()

app.layout = html.Div([
    dcc.Loading(
        id="loading",
        type="circle",
        children=dcc.Graph(id='hexagon-map', style={'height': '90vh'})
    ),
    html.Div(id='debug-info', style={'position': 'absolute', 'top': '10px', 'left': '10px', 'z-index': '1000', 'background': 'white', 'padding': '5px'})
])

@app.callback(
    [Output('hexagon-map', 'figure'),
     Output('debug-info', 'children')],
    Input('hexagon-map', 'relayoutData'),

)
def update_map(relayoutData):
    
    if relayoutData is None:
        zoom = 3
    else:
        zoom = relayoutData.get('mapbox.zoom', 3)
    
    # Map zoom to resolution
    if zoom < 5:
        resolution = 3
    elif zoom < 7:
        resolution = 4
    elif zoom < 9:
        resolution = 5
    elif zoom < 11:
        resolution = 6
    elif zoom < 13:
        resolution = 7 
    else:
        resolution = 8
    
    
    # Get the hex data for the chosen resolution
    geojson = hex_data[resolution]

    # Set up figure with Choroplethmapbox
    fig = go.Figure(go.Choroplethmapbox(
        geojson=geojson,
        locations=[feature["id"] for feature in geojson["features"]],  # Unique IDs for locations
        z=[feature["properties"]["population"] for feature in geojson["features"]],
        colorscale="Viridis",
        colorbar_title="Population",
        marker_opacity=0.5,
        marker_line_width=0
    ))
    
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            center=dict(lat=-1.286389, lon=36.817223),
            zoom=zoom,
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    debug_info = f"Zoom: {zoom:.1f}, Resolution: {resolution}"

    return fig, debug_info

if __name__ == '__main__':
    app.run_server(debug=True)







