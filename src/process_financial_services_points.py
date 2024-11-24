import geopandas as gpd 
import pandas as pd
import os
from geopy.geocoders import Nominatim
import time

RAW_DATA_DIR = '../../data/raw'
PROCESSED_DATA_DIR = '../../data/processed'

# Directory where the gpkg file for the financial services points is saved
FIN_POINTS_DIR = 'ken_financial_services_points'

def load_financial_services_points():
    print('[INFO] Attempting to load financial services points gpkg file...')
    file_name = 'ken_financial_services_points.gpkg'
    file_path = os.path.join(RAW_DATA_DIR, FIN_POINTS_DIR, file_name)
    financial_services_points = gpd.read_file(file_path)
    print('f[INFO] File found at {file_path}')
    print('f[INFO] Counties shapes loaded successfully!\n')
    financial_services_points.drop(['name:en', 'operator', 'network', 'addr:full', 'addr:city', 'source', 'name:sw'], axis=1, inplace=True)
    financial_services_points = extract_coordinates_from_geometry(financial_services_points)
    financial_services_points = lookup_places_osm(financial_services_points)
    financial_services_points = process_names(financial_services_points)
    financial_services_points['name'] = financial_services_points['name'].fillna('Name Not Listed')
    
    return financial_services_points

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

def lookup_places_osm(df):
    """
    Look up place names using OpenStreetMap's Nominatim for coordinates with missing names.
    """
    # Initialize geocoder
    geolocator = Nominatim(user_agent="ken_financial_services_points_app")
    
    df = df.copy()
    count = 0
    count_null_names_before = df['name'].isna().sum()
    print('[INFO] Attempting to fill out the null names in the financial services...')
    for idx in df[df['name'].isna()].index:
        lat = df.loc[idx, 'latitude']
        lng = df.loc[idx, 'longitude']
        
        try:
            # Reverse geocode the coordinates
            location = geolocator.reverse(f"{lat}, {lng}", exactly_one=True)
            
            if location:
                # Extract the name from address data
                address = location.raw.get('address', {})
                print(f"Address extracted = {address}")
                if 'amenity' in address:
                    print(f'[INFO] Amenity Name found!\n')
                    df.loc[idx, 'name'] = address['amenity']
            
            # Sleep to respect rate limits
            time.sleep(1)  # OpenStreetMap requires slower rates
            
            count += 1
            if count % 5 == 0:
                print(f"Processed {count} locations")
                
        except Exception as e:
            print(f"Error processing coordinates ({lat}, {lng}): {str(e)}")
            continue
    
    count_null_names_after = df['name'].isna().sum()
    print(f"Null values in the name column before processing = {count_null_names_before}")
    print(f"Null values in the name column after processing = {count_null_names_after}\n")
    return df

# Function to standardize bank names
def standardize_bank_name(df, pattern, standard_name):
    """
    Standardize bank names based on a pattern.
    
    Parameters:
    df: DataFrame containing bank names
    pattern: String pattern to match (e.g., 'KCB')
    standard_name: Name to replace matches with (e.g., 'KCB Bank')
    """
    if (type(pattern) == str):
        # Show current variations
        print(f"Current variations of names containing '{pattern}':")
        print(df[df['name'].str.contains(pattern, case=False, na=False)]['name'].unique())
        
        # Standardize the name
        df.loc[df['name'].str.contains(pattern, case=False, na=False), 'name'] = standard_name
        
        # Verify the change
        print(f"\nAfter standardization - all matched entries now show as '{standard_name}'")
        print(df[df['name'].str.contains(pattern, case=False, na=False)]['name'].unique())
    
    else:
        print("Processing multiple patterns at once")
        for pat in pattern:
            # Show current variations
            print(f"Current variations of names containing '{pat}':")
            print(df[df['name'].str.contains(pat, case=False, na=False)]['name'].unique())
            
            # Standardize the name
            df.loc[df['name'].str.contains(pat, case=False, na=False), 'name'] = standard_name
            
            # Verify the change
            print(f"\nAfter standardization - all matched entries now show as '{standard_name}'")
            print(df[df['name'].str.contains(pat, case=False, na=False)]['name'].unique())

    
    return df

def process_names(financial_services_points):
    # Renaming banks since a lot of them represent the same bank 
    financial_services_points.loc[financial_services_points['name'] == 'K C B', 'name'] = 'KCB Bank'
    financial_services_points = standardize_bank_name(financial_services_points, 'KCB', 'KCB Bank')
    financial_services_points = standardize_bank_name(financial_services_points, 'Kenya Commercial Bank', 'KCB Bank')

    financial_services_points = standardize_bank_name(financial_services_points, 'Stanbic', 'Stanbic Bank')
    financial_services_points = standardize_bank_name(financial_services_points, 'Family Bank', 'Family Bank')

    financial_services_points = standardize_bank_name(financial_services_points, 'Commercial Bank of', 'Commercial Bank of Africa')
    financial_services_points = standardize_bank_name(financial_services_points, 'Bank of Africa', 'Commercial Bank of Africa')
    financial_services_points = standardize_bank_name(financial_services_points, 'NIC Bank Limited', 'Commercial Bank of Africa')

    financial_services_points = standardize_bank_name(financial_services_points, 'CBK', 'Cooperative Bank of Kenya') 
    financial_services_points = standardize_bank_name(financial_services_points, 'Cooperative Bank', 'Cooperative Bank of Kenya') 
    financial_services_points = standardize_bank_name(financial_services_points, 'Co-operative Bank', 'Cooperative Bank of Kenya')

    financial_services_points = standardize_bank_name(financial_services_points, 'I&M', 'I&M Bank')

    financial_services_points = standardize_bank_name(financial_services_points, 'Post Bank', 'Kenya Post Office Savings Bank')
    financial_services_points = standardize_bank_name(financial_services_points, 'Postbank', 'Kenya Post Office Savings Bank')

    financial_services_points = standardize_bank_name(financial_services_points, 'Chase', 'Chase Bank')
    financial_services_points = standardize_bank_name(financial_services_points, 'ChaseBank', 'Chase Bank')

    financial_services_points = standardize_bank_name(financial_services_points, 'KWFT', 'Kenya Women Finance Trust')
    financial_services_points = standardize_bank_name(financial_services_points, 'Kenya Women Finance Trust', 'Kenya Women Finance Trust')

    financial_services_points = standardize_bank_name(financial_services_points, 'Trans National Bank', 'Access Bank Kenya')

    financial_services_points = standardize_bank_name(financial_services_points, 'National Bank', 'National Bank of Kenya')

    financial_services_points = standardize_bank_name(financial_services_points, 'Equity', 'Equity Bank')

    financial_services_points = standardize_bank_name(financial_services_points, 'Barclays', 'Barclays Bank')
    financial_services_points = standardize_bank_name(financial_services_points, 'Barcalys', 'Barclays Bank')


    financial_services_points = standardize_bank_name(financial_services_points, 'Co-Op Bank', 'Co-operative Bank of Kenya')
    financial_services_points = standardize_bank_name(financial_services_points, 'Co-op', 'Co-operative Bank of Kenya')
    financial_services_points = standardize_bank_name(financial_services_points, 'Co-', 'Co-operative Bank of Kenya')
    financial_services_points = standardize_bank_name(financial_services_points, ['Co operative', 'Co -', 'Co Op Bank', 'Co Op', 'Coop Bank'], 'Co-operative Bank of Kenya')

    financial_services_points = standardize_bank_name(financial_services_points, 'Ecobank', 'EcoBank')

    financial_services_points = standardize_bank_name(financial_services_points, 'Absa', 'Absa Bank')


    financial_services_points = standardize_bank_name(financial_services_points, 'DAIMOND', 'Diamond Trust Bank Group')
    financial_services_points = standardize_bank_name(financial_services_points, 'DTB', 'Diamond Trust Bank Group')
    financial_services_points = standardize_bank_name(financial_services_points, 'Diamond Trust Bank', 'Diamond Trust Bank Group')

    financial_services_points = standardize_bank_name(financial_services_points, 'Sacco', 'Savings and Credit Cooperative Organization')

    financial_services_points = standardize_bank_name(financial_services_points, 'M-Pesa', 'M-Pesa Point')
    financial_services_points = standardize_bank_name(financial_services_points, 'mpesa', 'M-Pesa Point')
    financial_services_points = standardize_bank_name(financial_services_points, ['Pesa', 'psea'], 'M-Pesa Point')

    financial_services_points = standardize_bank_name(financial_services_points, ['Kenya Women Finance', 'Kenya Woman Finance'], 'Kenya Women Finance Trust')
    financial_services_points = standardize_bank_name(financial_services_points, ['Kenya Women Micro', 'Kenya Woman Micro'], 'Kenya Women Microfinance Bank')

    # Rename all variations to "Posta" (post office)
    financial_services_points.loc[financial_services_points['name'].str.contains('Posta', case=False, na=False), 'name'] = 'POSTA'

    return financial_services_points


def main():
    financial_services_points = load_financial_services_points()

    try:
        export_filepath = os.path.join(PROCESSED_DATA_DIR, 'KEN_financial_services_points.csv')
        financial_services_points.to_csv(export_filepath, index=False)
        print(f"[INFO] H3 data augmented with all data successfully saved to {export_filepath}")
    except Exception as e:
        print(f"An error occurred while saving the DataFrame: {str(e)}")


if __name__ == "__main__":
    main()