import geopandas as gpd 
import matplotlib.pyplot as plt
import h3
import json
import folium
from geojson.feature import *

import branca.colormap as cm 
import folium
# import streamlit as st
# from streamlit_folium import folium_static
from folium import Map, Marker, GeoJson 



def load_population_data():
    gdf = gpd.read_file('../../data/kontur_population_KE_20231101.gpkg')
    
    return gdf

def hexagons_dataframe_to_geojson(df_hex, file_output = None, column_name = "population"):
    """
    Produce the GeoJSON for a dataframe, constructing the geometry from the "hex_id" column
    and with a property matching the one in column_name
    """    
    list_features = []
    
    for i,row in df_hex.iterrows():
        try:
            geometry_for_row = { "type" : "Polygon", "coordinates": [h3.h3_to_geo_boundary(h=row["h3"],geo_json=True)]}
            feature = Feature(geometry = geometry_for_row , id=row["h3"], properties = {column_name : row[column_name]})
            list_features.append(feature)
        except:
            print("An exception occurred for hex " + row["h3"]) 

    feat_collection = FeatureCollection(list_features)
    geojson_result = json.dumps(feat_collection)
    return geojson_result

def choropleth_map(df_aggreg, border_color = 'black', fill_opacity = 0.7, initial_map = None, with_legend = False,
                   kind = "linear"):   
    #colormap
    min_value = df_aggreg["population"].min()
    max_value = df_aggreg["population"].max()
    m = round ((min_value + max_value ) / 2 , 0)
    
    #take resolution from the first row
    res = h3.h3_get_resolution(df_aggreg.loc[0, 'h3'])
    
    if initial_map is None:
        initial_map = Map(location= [-1.286389, 36.817223], zoom_start=6, tiles="cartodbpositron", 
                attr= '© <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors © <a href="http://cartodb.com/attributions#basemaps">CartoDB</a>' 
            )
        

    #the colormap 
    #color names accepted https://github.com/python-visualization/branca/blob/master/branca/_cnames.json
    if kind == "linear":
        custom_cm = cm.LinearColormap(['green','yellow','red'], vmin=min_value, vmax=max_value)
    elif kind == "outlier":
        #for outliers, values would be -11,0,1
        custom_cm = cm.LinearColormap(['blue','white','red'], vmin=min_value, vmax=max_value)
    elif kind == "filled_nulls":
        custom_cm = cm.LinearColormap(['sienna','green','yellow','red'], 
                                      index=[0,min_value,m,max_value],vmin=min_value,vmax=max_value)
   

    #create geojson data from dataframe
    geojson_data = hexagons_dataframe_to_geojson(df_hex = df_aggreg)
    
    #plot on map
    name_layer = "Choropleth " + str(res)
    if kind != "linear":
        name_layer = name_layer + kind
        
    GeoJson(
        geojson_data,
        style_function = lambda feature: {
            'fillColor': custom_cm(feature['properties']['population']),
            'color': border_color,
            'weight': 1,
            'Highlight': True,
            'fillOpacity': fill_opacity 
        }, 
        name = name_layer
    ).add_to(initial_map)

    #add legend (not recommended if multiple layers)
    if with_legend == True:
        custom_cm.add_to(initial_map)   
    
    
    return initial_map




def main():
    gdf = load_population_data()
    print(gdf.head(10))
    # hexmap = choropleth_map(df_aggreg = gdf, with_legend = True, kind = "filled_nulls") 
    # Sidebar controls
    # st.sidebar.header("Map Controls")
    # num_hexagons = st.sidebar.slider("Number of hexagons to display", 100, len(gdf), 1000)
    # kind = st.sidebar.selectbox("Color scheme", ["linear", "outlier", "filled_nulls"])
    # with_legend = st.sidebar.checkbox("Show legend", value=True)

    # # Create and display map
    # st.write(f"Displaying {num_hexagons} hexagons")
    # hexmap = choropleth_map(df_aggreg=gdf[:num_hexagons], with_legend=with_legend, kind=kind)
    # folium_static(hexmap)


if __name__ == "__main__":
    main()