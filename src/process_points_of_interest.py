import geopandas as gpd 
import pandas as pd
import os
import h3
from shapely.geometry import Point
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time

RAW_DATA_DIR = '../../data/raw'
PROCESSED_DATA_DIR = '../../data/processed'

# Directory where the gpkg file for the points of interest is saved
POINTS_OF_INTEREST_DIR = 'ken_points_of_interest_points'
RAILWAYS_DIR = 'ken_railways_lines'
WATERWAYS_DIR = 'ken_waterways_lines'

def load_and_process_railways_data():
    print('[INFO] Attempting to load railways lines gpkg file...')
    file_name = 'ken_railways_lines.gpkg'
    file_path = os.path.join(RAW_DATA_DIR, RAILWAYS_DIR, file_name)
    railways_lines = gpd.read_file(file_path)
    railways_lines.drop(['name:en', 'ele', 'operator:type', 'layer', 'addr:full', 'addr:city', 'source', 'name:sw'], axis=1, inplace=True)
    railways_lines['name'] = railways_lines['name'].fillna('Name Not Listed')
    print('f[INFO] File found at {file_path}')
    print('f[INFO] Railways lines loaded successfully!\n')

    return railways_lines

def load_and_process_waterways_data():
    print('[INFO] Attempting to load waterways lines gpkg file...')
    file_name = 'ken_waterways_lines.gpkg'
    file_path = os.path.join(RAW_DATA_DIR, WATERWAYS_DIR, file_name)
    waterways_lines = gpd.read_file(file_path)
    waterways_lines.drop(['name', 'name:en', 'covered', 'width', 'depth', 'layer',
       'blockage', 'tunnel', 'natural', 'water', 'source', 'name:sw'], axis = 1, inplace=True)
    print('f[INFO] File found at {file_path}')
    print('f[INFO] Waterways lines loaded successfully!\n')
    return waterways_lines
    

def load_points_of_interest_data():
    print('[INFO] Attempting to load points of interest gpkg file...')
    file_name = 'ken_points_of_interest_points.gpkg'
    file_path = os.path.join(RAW_DATA_DIR, POINTS_OF_INTEREST_DIR, file_name)
    points_of_interest_points = gpd.read_file(file_path)
    print('f[INFO] File found at {file_path}')
    print('f[INFO] Points of interest loaded successfully!\n')

    return points_of_interest_points

def extract_coordinates_from_geometry(gdf):
    """
    Extract longitude and latitude from geometry column of a GeoDataFrame.
    
    Parameters:
    gdf (GeoDataFrame): Input GeoDataFrame with geometry column
    
    Returns:
    GeoDataFrame: Original GeoDataFrame with new longitude and latitude columns
    """
    # Create a copy to avoid modifying the original
    gdf = gdf.copy()
    
    # Extract coordinates
    gdf['longitude'] = gdf.geometry.centroid.x
    gdf['latitude'] = gdf.geometry.centroid.y
    
    # Verify the results
    print("Number of points processed:", len(gdf))
    print("Number of missing coordinates:", gdf[['longitude', 'latitude']].isna().any(axis=1).sum())
    
    return gdf

def extract_and_process_health_facilities_data(points_of_interest_points):
    health_amenities = ['pharmacy', 'clinic', 'hospital', 'veterinary', 'dispensary', 'dentist', '*', 'nursing_home', 'doctors', 'medical transport service','health_post', 'health_center','health_centre','pharmaccy','traditional health centre','veterinary_pharmacy', 'healthcare','clinic;hospital','health']
    health_facilities_points = points_of_interest_points[points_of_interest_points['amenity'].isin(health_amenities)]

    # Rename some amenities to standardize the naming
    health_facilities_points.loc[health_facilities_points['amenity'] == 'pharmaccy', 'amenity'] = 'pharmacy'
    health_facilities_points.loc[health_facilities_points['amenity'] == 'health_centre', 'amenity'] = 'health_center'
    health_facilities_points.loc[health_facilities_points['amenity'] == 'health', 'amenity'] = 'health_center'
    health_facilities_points.loc[health_facilities_points['amenity'] == 'healthcare', 'amenity'] = 'health_center'
    health_facilities_points.loc[health_facilities_points['amenity'] == 'clinic;hospital', 'amenity'] = 'clinic'

    health_facilities_points.drop(['name:en', 'man_made', 'shop', 'tourism',
       'opening_hours', 'beds', 'rooms', 'addr:full', 'addr:housenumber',
       'addr:street', 'addr:city', 'source', 'name:sw'], axis = 1, inplace=True)

    health_facilities_points = extract_coordinates_from_geometry(health_facilities_points)
    health_facilities_points['name'] = health_facilities_points['name'].fillna('Name Not Listed')

    return health_facilities_points

def extract_and_process_educational_facilities_data(points_of_interest_points):
    educational_amenities = ['school', 'driving_school', 'university', 'library', 'college', 'kindergarten']
    educational_facilities_points = points_of_interest_points[points_of_interest_points['amenity'].isin(educational_amenities)]
    educational_facilities_points.drop(['name:en', 'man_made', 'shop', 'tourism',
       'opening_hours', 'beds', 'rooms', 'addr:full', 'addr:housenumber',
       'addr:street', 'addr:city', 'source', 'name:sw'], axis = 1, inplace=True)

    educational_facilities_points = extract_coordinates_from_geometry(educational_facilities_points)
    educational_facilities_points['name'] = educational_facilities_points['name'].fillna('Name Not Listed')
    return educational_facilities_points

def extract_and_process_transportation_data(points_of_interest_points):
    transportation_amenities = ['bus_station', 'taxi', 'ferry_terminal', 'bus_stop', 'train_station', 'parking', 'bicycle_parking', 'parking_space', 'motorcycle_parking', 'car_rental', 'car_sharing', 'vehicle_inspection', 'bridge', 'ferry_terminal', 'taxi_stand', 'airport', 'harbor', 'railway_station', 'fuel', 'charging_station']
    transportation_points = points_of_interest_points[points_of_interest_points['amenity'].isin(transportation_amenities)]
    transportation_points.drop(['name:en', 'man_made', 'shop', 'tourism',
       'opening_hours', 'beds', 'rooms', 'addr:full', 'addr:housenumber',
       'addr:street', 'addr:city', 'source', 'name:sw'], axis = 1, inplace=True)

    transportation_points = extract_coordinates_from_geometry(transportation_points)
    transportation_points['name'] = transportation_points['name'].fillna('Name Not Listed')
    return transportation_points

def extract_and_process_public_amenities(points_of_interest_points):
    public_amenities = ['toilets', 'shower', 'drinking_water', 'fountain', 'waste_disposal', 'waste_transfer_station', 'waste_basket', 'recycling', 'street_lamp', 'telephone', 'clock',  'pond', 'sanitary_dump_station']
    public_amenities_points = points_of_interest_points[points_of_interest_points['amenity'].isin(public_amenities)]
    public_amenities_points.drop(['name', 'name:en', 'man_made', 'shop', 'tourism',
       'opening_hours', 'beds', 'rooms', 'addr:full', 'addr:housenumber',
       'addr:street', 'addr:city', 'source', 'name:sw'], axis = 1, inplace=True)

    public_amenities_points = extract_coordinates_from_geometry(public_amenities_points)
    return public_amenities_points

def extract_and_process_env_agr(points_of_interest_points):
    agr_env_amenities = [
    'grinding_mill', 'compost_site','water_or_irrigation', 'water_point', 'watering_place',
    'agriculture', 'green_house', 'gardens', 'farming', 'cattle_breeding', 'pump_house', 'ranger_station', 'animal_shelter'
    ]

    agr_env_points = points_of_interest_points[points_of_interest_points['amenity'].isin(agr_env_amenities)]
    agr_env_points.drop(['name', 'name:en', 'man_made', 'shop', 'tourism',
       'opening_hours', 'beds', 'rooms', 'addr:full', 'addr:housenumber',
       'addr:street', 'addr:city', 'source', 'name:sw'], axis = 1, inplace=True)
    agr_env_points = extract_coordinates_from_geometry(agr_env_points)

    return agr_env_points

def extract_and_process_food_beverage(points_of_interest_points):
    food_beverage_amenities = [
    'restaurant', 'cafe', 'bar', 'pub', 'fast_food', 'food_court', 'ice_cream', 'restaurant;bar', 'restaurant,bar', 'bbq', 'beer_garden', 'catering_service', 'food_outlet'
    ]

    food_beverage_points = points_of_interest_points[points_of_interest_points['amenity'].isin(food_beverage_amenities)]
    food_beverage_points.loc[food_beverage_points['amenity'] == 'pub', 'amenity'] = 'bar'
    food_beverage_points.loc[food_beverage_points['amenity'] == 'beer_garden', 'amenity'] = 'bar'
    food_beverage_points.loc[food_beverage_points['amenity'] == 'restaurant;bar', 'amenity'] = 'restaurant'
    food_beverage_points.loc[food_beverage_points['amenity'] == 'restaurant;bar', 'amenity'] = 'restaurant'
    food_beverage_points.loc[food_beverage_points['amenity'] == 'bbq', 'amenity'] = 'restaurant'

    food_beverage_points.drop(['name:en', 'man_made', 'shop', 'tourism',
       'opening_hours', 'beds', 'rooms', 'addr:full', 'addr:housenumber',
       'addr:street', 'addr:city', 'source', 'name:sw'], axis = 1, inplace=True)

    food_beverage_points = extract_coordinates_from_geometry(food_beverage_points)
    food_beverage_points['name'] = food_beverage_points['name'].fillna('Name Not Listed')
    
    return food_beverage_points

def extract_and_process_public_services(points_of_interest_points):
    public_services_amenities = [
    'police', 'fire_station', 'ambulance_station', 'courthouse', 'townhall', 'public_building', 'public_facility', 'social_centre', 'community_centre', 'social_facility', 'civic_service', 'prison', 'emergency_service', 'rescue_service'
    ]

    public_services_points = points_of_interest_points[points_of_interest_points['amenity'].isin(public_services_amenities)]
    public_services_points.loc[public_services_points['amenity'] == 'public_facility', 'amenity'] = 'public_building'
    public_services_points.loc[public_services_points['amenity'] == 'social_centre', 'amenity'] = 'social_facility'

    public_services_points.drop(['name:en', 'man_made', 'shop', 'tourism',
       'opening_hours', 'beds', 'rooms', 'addr:full', 'addr:housenumber',
       'addr:street', 'addr:city', 'source', 'name:sw'], axis = 1, inplace=True)

    public_services_points = extract_coordinates_from_geometry(public_services_points)
    public_services_points['name'] = public_services_points['name'].fillna('Name Not Listed')
    return public_services_points

def extract_and_process_leisure(points_of_interest_points):
    leisure_amenities = [
    'cinema', 'theatre', 'nightclub', 'club', 'gaming', 'arts_centre', 'exhibition_centre', 'leisure', 'music_venue', 'dance_club', 'gambling', 'sports_club', 'events_venue', 'studio', 'casino', 'internet_cafe'
    ]
    leisure_points = points_of_interest_points[points_of_interest_points['amenity'].isin(leisure_amenities)]
    leisure_points.drop(['name:en', 'man_made', 'shop', 'tourism',
       'opening_hours', 'beds', 'rooms', 'addr:full', 'addr:housenumber',
       'addr:street', 'addr:city', 'source', 'name:sw'], axis = 1, inplace=True)

    leisure_points = extract_coordinates_from_geometry(leisure_points)
    leisure_points['name'] = leisure_points['name'].fillna('Name Not Listed')
    return leisure_points

def extract_and_process_shopping_retail(points_of_interest_points):
    shopping_amenities = [
    'marketplace', 'shop', 'supermarket', 'butcher', 'butchery', 'shopping_mall', 'vending_machine', 'car_wash', 'bicycle_repair_station', 'hairdresser'
    ]
    shopping_retail_points = points_of_interest_points[points_of_interest_points['amenity'].isin(shopping_amenities)]
    shopping_retail_points.loc[shopping_retail_points['amenity'] == 'butchery', 'amenity'] = 'butcher'
    shopping_retail_points.drop(['name:en', 'man_made', 'shop', 'tourism',
       'opening_hours', 'beds', 'rooms', 'addr:full', 'addr:housenumber',
       'addr:street', 'addr:city', 'source', 'name:sw'], axis = 1, inplace=True)

    shopping_retail_points = extract_coordinates_from_geometry(shopping_retail_points)
    shopping_retail_points['name'] = shopping_retail_points['name'].fillna('Name Not Listed')
    return shopping_retail_points

def extract_and_process_religious_buildings(points_of_interest_points):
    religious_amenities = [
    'place_of_worship', 'church', 'mosque', 'monastery'
    ]
    religious_buildings_points = points_of_interest_points[points_of_interest_points['amenity'].isin(religious_amenities)]
    religious_buildings_points.drop(['name:en', 'man_made', 'shop', 'tourism',
       'opening_hours', 'beds', 'rooms', 'addr:full', 'addr:housenumber',
       'addr:street', 'addr:city', 'source', 'name:sw'], axis = 1, inplace=True)

    religious_buildings_points = extract_coordinates_from_geometry(religious_buildings_points)
    religious_buildings_points['name'] = religious_buildings_points['name'].fillna('Name Not Listed')
    return religious_buildings_points

def save_dataframe_to_csv(df, file_name):
    try:
        export_filepath = os.path.join(PROCESSED_DATA_DIR, file_name)
        df.to_csv(export_filepath, index=False)
        print(f"[INFO] H3 data augmented with all data successfully saved to {export_filepath}")
    except Exception as e:
        print(f"An error occurred while saving the DataFrame: {str(e)}")


def main():
    railways_lines = load_and_process_railways_data()
    waterways_lines = load_and_process_waterways_data()
    points_of_interest_points = load_points_of_interest_data()
    health_facilities_points = extract_and_process_health_facilities_data(points_of_interest_points)
    educational_facilities_points = extract_and_process_educational_facilities_data(points_of_interest_points)
    transportation_points = extract_and_process_transportation_data(points_of_interest_points)
    public_amenities_points = extract_and_process_public_amenities(points_of_interest_points)
    agr_env_points = extract_and_process_env_agr(points_of_interest_points)
    food_beverage_points = extract_and_process_food_beverage(points_of_interest_points)
    public_services_points = extract_and_process_public_services(points_of_interest_points)
    leisure_points = extract_and_process_leisure(points_of_interest_points)
    shopping_retail_points = extract_and_process_shopping_retail(points_of_interest_points)
    religious_buildings_points = extract_and_process_religious_buildings(points_of_interest_points)
     
    # Saving the different csvs
    save_dataframe_to_csv(railways_lines, 'KEN_railways_lines.csv')
    save_dataframe_to_csv(waterways_lines, 'KEN_waterways_lines.csv')
    save_dataframe_to_csv(health_facilities_points, 'KEN_health_facilities_points.csv')
    save_dataframe_to_csv(educational_facilities_points, 'KEN_educational_facilities_points.csv')
    save_dataframe_to_csv(transportation_points, 'KEN_transportation_points.csv')
    save_dataframe_to_csv(public_amenities_points, 'KEN_public_amenities_points.csv')
    save_dataframe_to_csv(agr_env_points, 'KEN_agr_env_points.csv')
    save_dataframe_to_csv(food_beverage_points, 'KEN_food_beverage_points.csv')
    save_dataframe_to_csv(public_services_points, 'KEN_public_services_points.csv')
    save_dataframe_to_csv(leisure_points, 'KEN_leisure_points.csv')
    save_dataframe_to_csv(shopping_retail_points, 'KEN_shopping_retail_points.csv')
    save_dataframe_to_csv(religious_buildings_points, 'KEN_religious_buildings_points.csv')


if __name__ == "__main__":
    main()