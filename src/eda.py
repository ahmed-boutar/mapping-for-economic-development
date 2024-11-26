'''
This script contains code that performs exploratory data analysis on the different datasets I have
'''
import geopandas as gpd 
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import rasterio
import numpy as np

def print_df_info(df, df_name):
    print(f"Data Structure for {df_name}")
    print("-"*10)
    print(f"Dimensions: {df.shape}")
    print(f"Data Types:\n{df.dtypes}")
    print(f"Missing Values:\n{df.isnull().sum()}")
    print(f"Unique observations:\n{df.nunique()}")
    print('\n')

def exploring_population_density():
    # function that runs EDA on the population density dataset
    gdf = gpd.read_file('../../data/raw/kontur_population_KE_20231101.gpkg')
    print("[INFO] EDA Population Density Dataset")
    print("Population Density Coordinate Reference System:")
    print(gdf.crs)
    print_df_info(gdf, 'Kontur Population Density')

def exploring_age_demographics_aggr():
    # function that runs EDA on the age demographics data after processing it and merging all the Raster files (.tif)
    df = pd.read_csv('../../data/processed/KEN_agesex_aggregated.csv')
    print("[INFO] EDA Age Demographics Aggregated Dataset\n")
    print("CRS of an example Raster file used for creating the aggregated dataset")
    with rasterio.open('../../data/raw/KEN_population_v2_0_agesex/KEN_population_v2_0_agesex_f0.tif') as src:
        # Read the data
        band1 = src.read(1)
        
        # Get metadata
        meta = src.meta
        print("="*15)
        print(meta)
        print("="*15)
        print('\n')

        
        # Print basic information
        print(f"Shape: {band1.shape}")
        print(f"Data type: {band1.dtype}")
        print(f"Minimum value: {np.min(band1)}")
        print(f"Maximum value: {np.max(band1)}")
        print(f"Mean value: {np.mean(band1)}")
   
    print_df_info(df, 'Aggregated Age Demographics')


def exploring_full_h3_dataset():
    """
    Perform comprehensive population and poverty analysis.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Input DataFrame with population and poverty data
    
    Returns:
    --------
    Generates multiple visualizations and prints key statistics
    """
    print('[INFO] EDA on the full H3 Dataset (augmented with all data)')
    df = pd.read_csv('../../data/processed/KEN_h3_data_full.csv')

    # 1. Population Distribution Analysis
    fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig1.suptitle('Population Distribution Analysis', fontsize=16)
    
    # Total Population Histogram and Box Plot
    sns.histplot(data=df, x='total_population', ax=ax1, kde=True, color='skyblue')
    ax1.set_title('Total Population Distribution')
    ax1.set_xlabel('Total Population')
    ax1.set_xlim(0, 50000)  # Zoom in to better visualize the distribution
    
    sns.boxplot(data=df, x='total_population', ax=ax2, color='lightgreen')
    ax2.set_title('Total Population Box Plot')
    ax2.set_xlabel('Total Population')
    ax2.set_xlim(0, 50000) 
    
    # 2. Stacked Population Distribution by County
    fig2, ax = plt.subplots(figsize=(16, 8))
    county_pop = df.groupby('county')[['total_male', 'total_female']].sum()
    county_pop.plot(kind='bar', stacked=True, ax=ax)
    ax.set_title('Population Distribution by County')
    ax.set_xlabel('County')
    ax.set_ylabel('Population')
    ax.legend(title='Gender')
    
    # 3. Population Distribution Percentage by County
    fig3, ax = plt.subplots(figsize=(12, 12))
    county_total_pop = df.groupby('county')['total_population'].sum()
    county_total_pop.plot(kind='pie', autopct='%1.1f%%', ax=ax)
    ax.set_title('Population Distribution Percentage by County')
    ax.set_xlabel('')
    ax.set_ylabel('')
    
    # 4. Nairobi Sub-County Population
    fig4, ax = plt.subplots(figsize=(12, 8))
    nairobi_data = df[df['county'] == 'Nairobi']
    nairobi_subcounty_pop = nairobi_data.groupby('sub_county')['total_population'].sum()
    nairobi_subcounty_pop.plot(kind='pie', autopct='%1.1f%%', ax=ax)
    ax.set_title('Population Distribution in Nairobi Sub-Counties')
    ax.set_xlabel('')
    ax.set_ylabel('')
    
    # 5. Poverty Analysis
    fig5, ax = plt.subplots(figsize=(12, 8))
    poverty_by_county_subcounty = df.groupby(['county', 'sub_county'])['In severe poverty '].first()
    severe_poverty_counts = poverty_by_county_subcounty[poverty_by_county_subcounty > 10].groupby('county').count()
    severe_poverty_counts.plot(kind='bar', ax=ax)
    ax.set_title('Number of Sub-Counties with Severe Poverty > 10%')
    ax.set_xlabel('County')
    ax.set_ylabel('Number of Sub-Counties')
    
    # Adjust layout and return figure objects
    plt.tight_layout()
    plt.show()


def exploring_points_of_interest():
    gdf = gpd.read_file('../../data/raw/ken_points_of_interest_points/ken_points_of_interest_points.gpkg')
    print('[INFO] EDA Points of Interests')
    print_df_info(gdf, 'points of interests in Kenya')
    print(f"Unique Amenities:\n {gdf['amenity'].value_counts()}")

def main():
    exploring_population_density()
    exploring_age_demographics_aggr()
    exploring_full_h3_dataset()
    exploring_points_of_interest()


if __name__ == "__main__":
    main()