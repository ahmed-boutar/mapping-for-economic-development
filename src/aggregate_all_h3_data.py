'''
This script is used to augment the h3 hexagons data with all the other spatial data I collected. 
This script will augment the h3 hexagons with with the names of counties and sub-counties they
belong to, poverty data for each county, crime rate based on the sub_county. 
The crime rate data will basically indicate whether that cell has a high_crime_rate in the county
it belongs to, which is based on a report published by a governmental agency in Kenya. 
This script will focus on adding this data to the merged dataframe with population data
and age demographics to produce a dataset with h3 hexagons that contain a lot of information.
'''
import geopandas as gpd 
import pandas as pd
import os
import h3
from shapely.geometry import Point

RAW_DATA_DIR = '../../data/raw'
PROCESSED_DATA_DIR = '../../data/processed'

# Directory where the shape files for the different administration levels in kenya are saved
ADM_SHP_DIR = 'ken_adm_iebc_20191031_shp'

def load_ken_counties_shp_file():
    print('[INFO] Attempting to load the county shape file...')
    file_name = 'ken_admbnda_adm1_iebc_20191031.shp'
    file_path = os.path.join(RAW_DATA_DIR, ADM_SHP_DIR, file_name)
    counties = gpd.read_file(file_path)
    print('f[INFO] File found at {file_path}')
    print('f[INFO] Counties shapes loaded successfully!\n')
    return counties

def load_ken_sub_counties_shp_file():
    print('[INFO] Attempting to load the sub-county shape file...')
    file_name = 'ken_admbnda_adm2_iebc_20191031.shp'
    file_path = os.path.join(RAW_DATA_DIR, ADM_SHP_DIR, file_name)
    sub_counties = gpd.read_file(file_path)
    print('f[INFO] File found at {file_path}')
    print('f[INFO] Sub-counties shapes loaded successfully!\n')
    return sub_counties

def load_process_ken_poverty_data():
    print('[INFO] Attempting to load poverty data file...')
    file_name = 'KEN_MPI_COUNTY_PROCESSED.csv'
    file_path = os.path.join(PROCESSED_DATA_DIR, file_name)
    poverty_df = pd.read_csv(file_path)
    print(f'[INFO] Succesfully loaded poverty data file found at {file_path}\n')
    poverty_df = poverty_df.rename(columns={'Subnational region': 'county'})
    poverty_df.drop(['Country', 'ISO country numeric code', 'ISO country code','World region'], axis=1, inplace=True)
    return poverty_df

def load_ken_highest_crimes_subcounties():
    print('[INFO] Attempting to load crimes subcounty data file...')
    file_name = 'KEN_county_subcounty_crime_2022.csv'
    file_path = os.path.join(PROCESSED_DATA_DIR, file_name)
    crimes_df = pd.read_csv(file_path)
    print(f'[INFO] Succesfully loaded crimes subcounty file found at {file_path}\n')
    crimes_df = crimes_df.rename(columns={'Subnational region': 'county'})
    return crimes_df

def get_county_from_coordinates(df, counties):
    geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
    h3_gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')

    # Perform spatial join
    # This will add all columns from counties to the H3 data
    result = gpd.sjoin(h3_gdf, counties, how='left', predicate='within')

    df['county'] = result['ADM1_EN']

    # Some hexagons are left unmatched so perform other operations to match them with a county
    unmatched_hexagons = df[df['county'].isna()].copy()
    geometry = [Point(xy) for xy in zip(unmatched_hexagons['longitude'], unmatched_hexagons['latitude'])]
    h3_gdf = gpd.GeoDataFrame(unmatched_hexagons, geometry=geometry, crs='EPSG:4326')
    intersect_match = gpd.sjoin(h3_gdf, counties, how='left', predicate='intersects')


    def assign_nearest_county(point, counties_gdf):
        # Calculate distance to all counties
        distances = counties_gdf.geometry.distance(point.geometry)
        # Get the county with minimum distance
        nearest_county = counties_gdf.iloc[distances.argmin()]
        return nearest_county['ADM1_EN']

    # For any hexagons still unmatched after intersects, find nearest county
    still_unmatched = intersect_match[intersect_match['ADM1_EN'].isna()]
    if len(still_unmatched) > 0:
        still_unmatched['nearest_county'] = still_unmatched.apply(
            lambda x: assign_nearest_county(x, counties), axis=1
        )

    df.loc[still_unmatched.index, 'county'] = still_unmatched['nearest_county']
    return df

def get_subcounty_from_coordinates(df, sub_counties):
    geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
    h3_gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')

    # Perform spatial join
    # This will add all columns from sub-counties to H3 data
    result = gpd.sjoin(h3_gdf, sub_counties, how='left', predicate='within')

   
    original_columns = list(df.columns)
    df['sub_county'] = result['ADM2_EN']

    # Some hexagons are left unmatched so perform other operations to match them with a county
    unmatched_hexagons = df[df['sub_county'].isna()].copy()
    geometry = [Point(xy) for xy in zip(unmatched_hexagons['longitude'], unmatched_hexagons['latitude'])]
    h3_gdf = gpd.GeoDataFrame(unmatched_hexagons, geometry=geometry, crs='EPSG:4326')
    intersect_match = gpd.sjoin(h3_gdf, sub_counties, how='left', predicate='intersects')

    print(f"Number of unmatched hexagons = {len(unmatched_hexagons)}")
    print(f"Number of intersect matches = {len(intersect_match)}")
    
    def assign_nearest_sub_county(point, sub_counties_gdf):
        # Calculate distance to all sub-counties
        distances = sub_counties_gdf.geometry.distance(point.geometry)
        # Get the sub-county with minimum distance
        nearest_county = sub_counties_gdf.iloc[distances.argmin()]
        return nearest_county['ADM2_EN']

    # For any hexagons still unmatched after intersects, find nearest county
    still_unmatched = intersect_match[intersect_match['sub_county'].isna()]
    if len(still_unmatched) > 0:
        still_unmatched['nearest_sub_county'] = still_unmatched.apply(
            lambda x: assign_nearest_sub_county(x, sub_counties), axis=1
        )

    df.loc[still_unmatched.index, 'sub_county'] = still_unmatched['nearest_sub_county']
    return df

def main():
    counties = load_ken_counties_shp_file()
    sub_counties = load_ken_sub_counties_shp_file()

    # Load the h3 data with age_demographics and population data
    h3_data_file_path = os.path.join(PROCESSED_DATA_DIR, 'KEN_population_age_demographics_merged.csv')
    h3_data = pd.read_csv(h3_data_file_path)

    # Augment h3 data with the names of counties and subcounties they belong to
    h3_df_county = get_county_from_coordinates(h3_data.copy(), counties.copy())
    h3_df_all_adm = get_subcounty_from_coordinates(h3_df_county.copy(), sub_counties.copy())

    # Augment h3 data with poverty data (MPI)
    poverty_df = load_process_ken_poverty_data()
    h3_with_poverty = h3_df_all_adm.merge(poverty_df, on='county', how='left')

    # Augment h3 data with crimes for subcounties by creating a new boolean column 
    # Column is set to 1 if the subcounty the h3 hexagon belongs to figure in the crimes 
    crimes_sub_counties = load_ken_highest_crimes_subcounties()
    h3_with_poverty['sub_county'] = h3_with_poverty['sub_county'].str.strip().str.lower()
    crimes_sub_counties['sub-county'] = crimes_sub_counties['sub-county'].str.strip().str.lower()

    # Add the 'high_crime_in_county' column with default value of 0
    h3_with_poverty['high_crime_in_county'] = 0

    # Update 'high_crime_in_county' to 1 for matches in crimes subcounties data
    h3_with_poverty.loc[h3_with_poverty['sub_county'].isin(crimes_sub_counties['sub-county']), 'high_crime_in_county'] = 1

    try:
        export_filepath = os.path.join(PROCESSED_DATA_DIR, 'KEN_h3_data_full.csv')
        h3_with_poverty.to_csv(export_filepath, index=False)
        print(f"[INFO] H3 data augmented with all data successfully saved to {export_filepath}")
    except Exception as e:
        print(f"An error occurred while saving the DataFrame: {str(e)}")

if __name__ == "__main__":
    main()