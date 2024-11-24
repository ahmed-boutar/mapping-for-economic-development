import rasterio
import pandas as pd
import numpy as np
import h3
import os
import re
from functools import reduce

RAW_DATA_DIR = '../../data/raw'
PROCESSED_DATA_DIR = '../../data/processed'

AGE_DEMOGRAPHICS_DIR = 'KEN_population_v2_0_agesex'

def get_file_names(directory):
    """Gets the names of all files in a directory."""
    file_names = []
    for entry in os.scandir(directory):
        if entry.is_file():
            file_names.append(entry.name)
    return file_names

def filter_files(file_names):
    """
    Process a list of population file names and create a dictionary mapping
    file names to their corresponding features.

    Parameters:
    file_list (list): List of file names

    Returns:
    dict: Dictionary with file names as keys and features as values
    """
    result = {}
    pattern = r'KEN_population_v2_0_agesex_([fm]\d+)\.tif$'

    for file_name in file_names:
        match = re.search(pattern, file_name)
        if match:
            feature = match.group(1)
            result[file_name] = feature

    return result


def extract_tif_data(filename, file_feature):
    with rasterio.open(filename) as src:
            band1 = src.read(1)  # Read the first band (population data)
            transform = src.transform  # Get the affine transformation

    # Prepare a list to hold the data
    data = []

    # Get dimensions of the raster
    height, width = band1.shape

    # Loop through each pixel in the raster
    for row in range(height):
        for col in range(width):
            # Get the population value for this pixel
            population_value = band1[row, col]

            # Skip no-data values if necessary (depending on your raster)
            if population_value != src.nodata:
                # Convert pixel coordinates to geographic coordinates
                lon, lat = transform * (col, row)  # (x, y) = (col, row)

                # Append the data as a tuple
                data.append((population_value, lon, lat))
    # Create a DataFrame
    df_population = pd.DataFrame(data, columns=[f'population_{file_feature}', 'lon', 'lat'])

    # Optionally, reset the index
    df_population.reset_index(drop=True, inplace=True)
    return df_population


def gis_df_to_h3_df(df, population_column_name):
    print(f'Processing df for {population_column_name}')
    resolution = 8
    try:
        df_h3 = df.copy()
        df_h3['h3'] = df.apply(lambda row: h3.geo_to_h3(row["lat"], row["lon"], resolution), axis = 1) 
        df_h3_agg = df_h3.groupby("h3")[population_column_name].sum().reset_index() 
        print("Successfuly created the h3 df")
    except:
        print("An error has occured while converting lat and lon to h3")
    
    return df_h3_agg

def create_df_list_from_directory(file_names_dict):
    # Open the raster file
    df_list = []
    for filename in file_names_dict:
        try:
            print(f'Processing file: {filename}')
            filepath = os.path.join(RAW_DATA_DIR, AGE_DEMOGRAPHICS_DIR, filename)
            df_file = extract_tif_data(filepath, file_names_dict[filename])
            print(f'Successfully created a df from file: {filename}')
            print(f'Columns of the resulting df: {df_file.columns}')
            print(f'{filename} df info:\n')
            print(df_file.head(5))
            print(f'Saving dataframe from file {filename}')
            save_dataframe_to_csv(df_file, f'../output/df_tif_files/df_KEN_agesex_{file_names_dict[filename]}.csv')
            print(f'Successfully saved tif dataframe as csv')
            df_h3 = gis_df_to_h3_df(df_file, df_file.columns[0])
            print(f'Saving H3 dataframe for {df_file.columns[0]}')
            save_dataframe_to_csv(df_file, f'../output/df_h3/df_KEN_agesex_{df_file.columns[0]}.csv')
            print(f'Successfully saved H3 dataframe as csv')
            df_list.append(df_h3)
        except:
            print(f"An error has occured while processing the file: {filename}")
    
    return df_list

def join_dataframes_on_h3(dataframe_list):
    """
    Join multiple DataFrames based on the 'h3' column.
    
    Parameters:
    dataframe_list (list): List of pandas DataFrames to join
    
    Returns:
    pandas.DataFrame: Joined DataFrame
    """
    # Check if the list is empty
    if not dataframe_list:
        return pd.DataFrame()
    
    # Function to perform the join
    def join_two_dataframes(left, right):
        return pd.merge(left, right, on='h3', how='outer')
    
    # Use reduce to apply the join function to all DataFrames in the list
    joined_df = reduce(join_two_dataframes, dataframe_list)
    
    return joined_df

def save_dataframe_to_csv(dataframe, filepath):
    """
    Save a DataFrame to a CSV file.
    
    Parameters:
    dataframe (pandas.DataFrame): DataFrame to save
    filepath (str): Path where the CSV file should be saved
    
    Returns:
    None
    """
    try:
        dataframe.to_csv(filepath, index=False)
        print(f"DataFrame successfully saved to {filepath}")
    except Exception as e:
        print(f"An error occurred while saving the DataFrame: {str(e)}")

def create_agregate_df_age_sex():
    data_dir = os.path.join(RAW_DATA_DIR, AGE_DEMOGRAPHICS_DIR)
    file_names = get_file_names(data_dir)
    file_names_dict = filter_files(file_names=file_names)
    df_h3_list = create_df_list_from_directory(file_names_dict)
    df_age_sex_aggr = join_dataframes_on_h3(df_h3_list)
    return df_age_sex_aggr


def main():
    df_age_sex_aggr = create_agregate_df_age_sex()
    output_path = os.path.join(PROCESSED_DATA_DIR, 'KEN_agesex_aggregated.csv')
    save_dataframe_to_csv(df_age_sex_aggr, output_path)

if __name__ == "__main__":
    main()