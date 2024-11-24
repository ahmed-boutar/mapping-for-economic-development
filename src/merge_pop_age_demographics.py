import geopandas as gpd 
import pandas as pd
import os
import h3

RAW_DATA_DIR = '../../data/raw'
PROCESSED_DATA_DIR = '../../data/processed'

def load_age_demographics():
    print('[INFO] Attempting to read the age demographics data..')
    file_name = 'KEN_agesex_aggregated.csv'
    file_path = os.path.join(PROCESSED_DATA_DIR, file_name)
    age_demographics_df = pd.read_csv(file_path)
    print(f'[INFO] File found at {file_path}!\n')
    print('[INFO] Successfully loaded the age demographics data!\n')
    return age_demographics_df

def load_population():
    print('[INFO] Attempting to read the population data..')
    file_name = 'kontur_population_KE_20231101.gpkg'
    file_path = os.path.join(RAW_DATA_DIR, file_name)
    population_df = gpd.read_file(file_path)
    print(f'[INFO] File found at {file_path}!\n')
    print('[INFO] Successfully loaded the population data!\n')
    return population_df
    
def get_pop_total_and_sum(df):
    total_pop = df['total_population'].round().astype(int)
    sum_gender = (df['total_male'].round().astype(int) + df['total_female'].round().astype(int))

    # Count the number of rows where they match
    matching_rows = (total_pop == sum_gender).sum()
    return total_pop, sum_gender, matching_rows

def process_population_data(df):
    """
    Process population data by:
    1. Filling missing population values with sum of demographic columns
    2. Creating total male and female population columns
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing population data
    
    Returns:
    pandas.DataFrame: Processed DataFrame with new columns
    """
    # Create a copy to avoid modifying the original
    processed_df = df.copy()
    
    # Get all demographic columns (excluding 'h3', 'population', and 'geometry')
    demographic_cols = [col for col in df.columns 
                       if col.startswith('population_') 
                       and col != 'population']
    
    # Fill missing population values with sum of demographic columns
    processed_df['population'] = processed_df['population'].fillna(
        processed_df[demographic_cols].sum(axis=1)
    )
    
    # Create total male population column
    male_cols = [col for col in df.columns if col.startswith('population_m')]
    processed_df['total_male'] = processed_df[male_cols].sum(axis=1).round().astype(int)
    
    # Create total female population column
    female_cols = [col for col in df.columns if col.startswith('population_f')]
    processed_df['total_female'] = processed_df[female_cols].sum(axis=1).round().astype(int)

    processed_df.rename(columns={'population': 'total_population'}, inplace=True)
    processed_df.drop('geometry', axis=1, inplace=True)

    total_pop, sum_gender, matching_rows = get_pop_total_and_sum(processed_df)

    print(f"Number of rows where total population equals sum of gender totals: {matching_rows}")

    # negative value indicates that the sum is bigger than the recorded total pop from first dataset 
    # positive value indicates that the recorded total pop from first dataset is bigger than the sum
    processed_df['recorded_pop_diff'] = total_pop - sum_gender

    #Update the total_population to capture the max number of population 
    # Do this before update to keep the original difference recorded
    # Create the condition where sum is bigger than total population
    condition = (processed_df['total_male'] + processed_df['total_female']) > processed_df['total_population']

    # Replace population where condition is True
    processed_df.loc[condition, 'total_population'] = processed_df.loc[condition, 'total_male'] + processed_df.loc[condition, 'total_female']
    total_pop, sum_gender, matching_rows = get_pop_total_and_sum(processed_df)
    print(f"Number of rows where total population equals sum of gender totals after update: {matching_rows}")
    return processed_df


def merge_and_process_age_demographics_and_pop(population_df, age_demographics_df):
    def get_h3_center(h3_index):
        # h3.h3_to_geo returns (lat, lng)
        lat, lng = h3.h3_to_geo(h3_index)
        return pd.Series({'latitude': lat, 'longitude': lng})
    
    print('[INFO] Merging and processing age demographics and population data...')
    population_df = population_df.to_crs(epsg=4326)
    df_merged = age_demographics_df.merge(population_df, on='h3', how='left')
    print('[INFO] Merging Complete!')
    df_merged_clean = process_population_data(df_merged)
    
    # Apply the function to create new columns
    df_merged_clean[['latitude', 'longitude']] = df_merged_clean['h3'].apply(get_h3_center)
    print('[INFO] Processing Complete!')
    return df_merged_clean


def main():
    age_demographics_df = load_age_demographics()
    population_df = load_population()
    age_demographics_pop_df = merge_and_process_age_demographics_and_pop(population_df, age_demographics_df)

    # Defining the export file path to save the dataframe
    export_filepath = os.path.join(PROCESSED_DATA_DIR, 'KEN_population_age_demographics_merged.csv')

    # Attempting to save the dataframe
    try:
        age_demographics_pop_df.to_csv(export_filepath, index=False)
        print(f"[INFO] Merged dataframe of age demographics and population successfully saved to {export_filepath}")
    except Exception as e:
        print(f"An error occurred while saving the DataFrame: {str(e)}")

if __name__ == "__main__":
    main()