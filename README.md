# Mapping for Economic Development (KENYA)

## Project Overview
This project aims to curate and open source a novel dataset aimed at fostering
economic development in Africa, with an initial focus on Kenya. The dataset will combine
various geographical and demographic data to enable businesses, researchers, and possibly lawmakers to make better informed decisions, conduct valuable analyses, and have a better understanding and overview of the geographical area of their choosing.
This project curates and open sources a novel dataset designed to foster economic development in Africa, starting with Kenya. By combining geospatial and demographic data, this dataset's goal is to enable businesses, researchers, and policymakers to make data-driven decisions, conduct meaningful analyses, and gain detailed insights into specific geographical areas (all relevant data in one place).

## Folder Structure
```
mapping-for-economic-development/
├── LICENSE.txt
├── README.md
├── .gitignore
├── requirements.txt
├── src/
│   ├── aggregate_age_demographics.py
│   ├── aggregate_all_h3_data.py
│   ├── merge_pop_age_demographics.py
│   ├── process_financial_services_points.py
│   ├── process_points_of_interest.py
data/ # data to be downloaded from the open-source dataset
├── raw
├── processed
```


### Scripts contents 

- `aggregate_age_demographics.py`: This script processes the files in the folder `raw/KEN_population_v2_0_agesex`. It loads all the .tif files, extracts the data corresponding to each age range along with the coordinates (which it converts to a different map projection if needed) and creates a column with the h3 indices. Once all the files have been processed, it outputs a csv with all the data merged on the h3 IDs. The output csv will have a list of h3 hexagons with the age demographics (number of males/females under specific age), named `KEN_age_sex_aggregated.csv`.
- `merge_pop_age_demographics.py`: This script reads the data from the file `kontur_population_KE_20231101`, which contains a list of h3 hexagons at a 400m resolution with population data. It then merges the output of the `aggregate_age_demographics.py` with the population dataset to output a new csv `KEN_population_age_demographics_merged`, which contains a list of h3 hexagons, the population in each hexagon and the age distribution within each hexagon (approximation).
- `aggregate_all_h3_data.py`: This script loads `KEN_population_age_demographics_merged` dataset and adds more data to the h3 hexagons. First, it uses the Shape Files of the different administration levels found under `raw/ken_adm_iebc_20191031_shp` to extract the name of counties and sub-counties that each hexagon belongs to. It then uses the MPI (poverty index) data found under `processed/KEN_MPI_COUNTY_PROCESSED.csv`, which included the poverty index (and other information) for each county, to add poverty data to each hexagon. Lastly, it uses the crimes data found under `processed/KEN_county_subcounty_crime_2022`, which includes the subcounties that have the highest crime rate (relative to the county itself), to determine whether a hexagon has a high crime rate relative to the county it belongs to. 
- `process_financial_services_points.py`: This scripts loads the data found under `raw/ken_financial_services_points`, extracts the coordinates for every data point, cleans the dataset (by dropping columns that have mostly missing values) and tries to fill null values for names and then exports the processed version to `processed/KEN_financial_services_points.csv`
- `process_points_of_interest.py`: This script loads the points of interest data found under `raw/ken_points_of_interest_points`. It then extracts data based on the amenities each observation represents. For example, observations that contain amenities like 'hospital' would be included in the health facilities data. This script also loads railways data and waterways data (GIS data) found under `raw/ken_railways_lines` and `raw/ken_waterways_lines` respectively. This script then exports all this data

## Executive Summary

The project aims to create a comprehensive geospatial dataset mapping population density, age demographics, and other socioeconomic data to H3 hexagons, a geospatial indexing system using a hexagonal grid structure. This approach facilitates detailed analyses and supports the creation of affluence scores, empowering businesses to identify high-potential expansion areas. Policymakers and researchers also benefit by gaining actionable insights into geographic regions, improving decision-making for development initiatives. Future iterations aim to include environmental and soil usage data, enabling research into food security and climate change impacts. Visualizing this data through interactive dashboards (e.g., using Plotly) would further enhance accessibility for businesses, researchers, and the public. While the initial focus is on Kenya, the long-term vision is to scale the dataset to other African countries.

### Motivation

Coming from Tunisia, a small country in North Africa, I have observed firsthand the disparities
in development across different regions in my country. Traveling to Kenya and Tanzania
made me realized that these disparities were common in a lot of African countries. Therefore,
I decided to curate this dataset, hoping to enable research and initiatives that might support
economic development across the continent.
Having all this different data in one place would enable businesses to come up with affluence
scores, allowing them to make more informed expansion decisions. Since a lot of proxy data for affluency have licenses around it that prevent the dataset from being open-sourced, my goal was to include as much data that can paint a clearer picture about the socio-economical state of different countries. Some of this data would include the location of railways, waterways, crime data etc...
The starting point for this project will be Kenya, given its more developed IT and industrial
sectors, as well as the availability of the data I aim to collect.

### Potential Applications
- **Business Expansion and Market Analysis**: Companies can use the affluence scores derived from this dataset to identify underserved regions with growth potential, optimizing expansion strategies in Kenya and, eventually, other African countries.

- **Urban Planning and Infrastructure Development**: Policymakers can leverage the dataset to prioritize investments in infrastructure, such as transportation networks and utilities, focusing on regions with high poverty indices or low access to amenities.

- **Research on Food Security and Climate Change:**
Incorporating environmental data will allow researchers to assess the impact of land use, climate patterns, and resource availability on food security, aiding in the design of sustainable agricultural practices.

- **Crime Prevention and Public Safety:** Geospatial mapping of crime data could authorities identify high-risk areas and deploy targeted safety initiatives, improving the overall quality of life in vulnerable regions.

- **Sustainable Development Goals (SDG) Monitoring:** Researchers can use the dataset to measure progress toward SDGs, such as poverty reduction, quality education, and sustainable cities, providing data-driven assessments for international organizations.

- **Education and Social Services Allocation:** By integrating demographic data, NGOs and governments can allocate resources like schools, hospitals, and social services more effectively to areas in need.

### Unique Approach and Existing Solutions
While there are existing datasets that map global population or building footprints to geographical locations, such as Microsoft ML Building Footprints or WorldPop, none integrate all the dimensions proposed in this project. The closest comparable solution is Kontur, which provides geospatial data analysis, including the Kontur Population Dataset (offering 3km-resolution H3 hexagons). However, most Kontur datasets are proprietary, with subscriptions costing up to $1,000 per month, making them inaccessible to many researchers, businesses, and policymakers. Some datasets are made available by ESRI, but the usage is limited due to the licensing around it (and it costs money).

This project sets itself apart by synthesizing disparate sources like WorldPop and The Humanitarian Data Exchange into a cohesive, multi-faceted, open-source dataset. The use of the H3 hexagon grid system further distinguishes it, offering advantages over traditional GIS techniques:

- Scalability: H3 hexagons allow for multi-resolution analysis, from local neighborhoods to nationwide coverage, without the distortion inherent in square grids.
- Flexibility: The H3 system seamlessly integrates population and age demographics, while allowing for the addition of complementary datasets like points of interest (POIs), poverty indices, and crime rates by sub-counties (different administration level).
- Granularity: By working with 400m hexagons, this project achieves a higher resolution than other openly available datasets, ensuring more precise spatial analyses.

Additionally, the inclusion of data beyond traditional population metrics—such as POIs, financial service locations, poverty, and crime data makes this dataset uniquely multi-dimensional. This integration creates a single-source dataset that reduces the overhead required for geospatial data analysis, making it easier for users to extract insights and build applications that support economic development.

## Data Description

### Content Description
The data collected comes from different sources, serve different purposes, and have been utilized in different ways. In this section, we will discuss the raw data and how it was sourced and then cover details about the processed data. Please note that all data sourced from the Humanitarian Data Exchange is shared under Creative Commons Attribution International license, allowing the public use of the datasets. 

#### Raw Data 
Most of the data was sourced from Humanitarian Data Exchange. To learn more about their review process and other details pertaining to data collection, please visit: [Humanitarian OpenStreetMap Team](https://www.hotosm.org/tools-and-data/data-principles/)

**Kenya: Population Density for 400m H3 Hexagons**
<br>

- This dataset contains data about the population density at a 400m resolution. It was "built from Kontur Population: Global Population Density for 400m H3 Hexagons Vector H3 hexagons with population counts at 400m resolution". What makes this dataset more accurate than others found on the web is the fact that the data was scaled and population density was updated using "GHSL, Facebook, Microsoft Buildings, Copernicus Global Land Service Land Cover, and OpenStreetMap data". This might be one of the few datasets made available to the public by Kontur, which usually has data available using a subscription. The dataset downloaded was released on Nov 01, 2023. It contains the hexagons at resolution 8 that cover all of Kenya, with the population density associated with it. Note, some areas in Kenya were not covered by the dataset given that they were determined to be unpopulated areas. [Source: Population Density for 400m H3 Hexagons](https://data.humdata.org/dataset/kontur-population-kenya?)

**Kenya: Age Demographics (agesex)**
<br>

- This dataset is a sharded dataset, where each file in a .tif format, contains the number of males or females under a specific age, with coordinates representing the areas covered by the data point. The file names are in the following format: KEN_population_v2_0_agesex_{sex_age}.tif, where sex can either be "f" for female and "m" for male, while the age is a number, representing the number of people under that age. The dataset contains 40 Raster files (.tif). It was made available through the efforts of WorldPop Research Group at the University of Southampton. Citation: Gadiaga A. N., Abbott T. J., Chamberlain H., Lazar A. N., Darin E., Tatem A. J. 2023. Census disaggregated gridded population estimates for Kenya (2022), version 2.0. University of Southampton. doi:10.5258/SOTON/WP00762
- Note: this dataset has a Creative Commons Attribution 4.0 International (cc-by-sa) license, allowing public use of the data with citation. 
- Note 2: "While this data represents population counts, values
contain decimals, i.e. fractions of people. This is because both the input population data and age-sex proportions contain decimals. For this reason, it is advised to aggregate the rasters at a coarser scale. For example, if four grid cells next to each other have values of 0.25 this indicates that there is 1 person of that age group somewhere in those four grid cells"
- The projection for all GIS files is the geographic coordinate system WGS84 (World Geodetic System 1984).
- To read more about the provenance and sourcing behind this dataset, please visit read the [release statement](https://data.worldpop.org/repo/wopr/KEN/population/v2.0/KEN_population_v2_0_README.pdf).
- This data is made available on the WorldPop website, specifically in their data repo which you can access and download [here](https://data.worldpop.org/repo/wopr/KEN/population/v2.0/KEN_population_v2_0_README.pdf)

**Kenya Railways**
<br>

- This dataset contains the location of the different railways in Kenya. This dataset was last updated on Nov 1 2024, and is updated every month by the Humanitarian OpenStreetMap Team (HOT).  This dataset was downloaded in a .gpkg format where every observation is a Line (geometry), delimiting where the railway line starts and end.[Source: Kenya Railways Data](https://data.humdata.org/dataset/hotosm_ken_railways)

**Kenya Waterways**
<br>

- This dataset contains the location of the different waterways that exist in Kenya, including the type of waterway (lake, river, etc...). This dataset was last updated on Nov 1 2024, and is updated every month by the Humanitarian OpenStreetMap Team (HOT).  This dataset was downloaded in a .gpkg format where every observation is a Line (geometry), delimiting where the waterway body starts and end. Note that this dataset can be downloaded in a different geometry like Polygon or Point, which can give a more granular view of the waterways. For the sake of this project and mapping all this data, using the dataset with LINE gemoetry would be more suitable. [Source: Kenya Railways Data](https://data.humdata.org/dataset/hotosm_ken_waterways)

**Kenya Financial Services**
<br>

- This dataset was made available through the efforts of Humanitarian OpenStreetMap Team and was made available on the Humanitarian Data Exchange. This dataset contains the location of the different financial services in Kenya. Not only does it include the location and name of each financial service, but it also includes the type (bank, ATM, post_office...). This dataset was last updated on Nov 1 2024, and is updated every month by the Humanitarian OpenStreetMap Team (HOT). Details on the exact data collection process were not included in the source. However, since the source is Humanitarian Data Exchange, we can safely assume that the data was thoroughly reviewed. This dataset was downloaded in a .gpkg format where every observation is a Point (geometry). [Source: Kenya Financial Services](https://data.humdata.org/dataset/hotosm_ken_financial_services)

**MPI (Multidimensional Poverty Index) and Partial Indices Subnational Database**
<br>

- This dataset was made available through the efforts of Humanitarian OpenStreetMap Team and was made available on the Humanitarian Data Exchange. It contains MPI data from Jan 01 1993 to Dec 31 2023. The dataset was last updated in Nov 24, 2024. Description of the dataset from the source: "The index provides the only comprehensive measure available for non-income poverty, which has become a critical underpinning of the SDGs. Critically the MPI comprises variables that are already reported under the Demographic Health Surveys (DHS) and Multi-Indicator Cluster Surveys (MICS) The resources subnational multidimensional poverty data from the data tables published by the Oxford Poverty and Human Development Initiative (OPHI), University of Oxford. The global Multidimensional Poverty Index (MPI) measures multidimensional poverty in over 100 developing countries, using internationally comparable datasets and is updated annually. The measure captures the severe deprivations that each person faces at the same time using information from 10 indicators, which are grouped into three equally weighted dimensions: health, education, and living standards. The global MPI methodology is detailed in Alkire, Kanagaratnam & Suppa (2023)". Note that this dataset contains the multidimensional poverty indices for every country in the world (at the subnational level, meaning at a county or state level). The data comes in an Excel file (tabular data) with multiple sheets. The work done on this dataset includes extracting data pertaining to Kenya and going through the different sheets to get the relevant data for this project. [Source: MPI and Partial Indices Subnational Database](https://data.humdata.org/dataset/global-mpi/resource/45b18fbb-ab0d-4f54-ae23-c078f1eccf25)

**Kenya Points of Interests (POIs)**
<br>

- This dataset was made available through the efforts of Humanitarian OpenStreetMap Team and was made available on the Humanitarian Data Exchange. It contains the geospatial locations of the different points of interests in Kenya. Points of Interests include hospitals, schools, financial services, leisure and entertainement points etc... This dataset was downloaded in a .gpkg format where every observation is a Point (geometry), identifying the location where the point of interest lies in Kenya. Note that this dataset can be downloaded in a different geometry like Polygon. For the sake of this project and mapping all this data, using the dataset with Point gemoetry would be more suitable as it gives a more granular overview of the different points of interest. 
- The dataset contains features like 'amenity', which delimits the type of amenity the point of interest represents. Examples include hospital, school, cinema, restaurant etc... 
- The processing done on the dataset aimed to extract the different datapoints based on the "segment" they represent. For example, data points that represent amenities such as 'pharmacy', 'clinic', 'hospital', 'veterinary' will all be extracted and saved as health services. 
- This dataset also includes financial services data, but when performing EDA, I realized that the financial services points dataset (mentioned above) is more complete and provides a more comprehensive overview.
- This dataset was last updated on Nov 1 2024, and is updated every month by the Humanitarian OpenStreetMap Team (HOT) [Kenya Points of Interests (POIs)](https://data.humdata.org/dataset/hotosm_ken_points_of_interest)

**Kenya - Subnational Administrative Boundaries**
<br>

- This dataset contains the shape files (.shp) delimiting each county and sub-county in Kenya. In other words, it provides boundaries of each administrative level in Kenya from national to subnational level (i.e sub-counties). The specific shape files downloaded were updated on Feb 20, 2020. Since the administrative boundaries are pretty much set, it is safe to assume that using this data will provide an accurate representation of the boundaries in Kenya. This dataset was used to augment the h3 hexagons and determine what county and sub-county they belong to. [Source: Kenya - Subnational Administrative Boundaries](https://data.humdata.org/dataset/cod-ab-ken)

**Kenya Cell Tower Locations**
<br>

- This dataset contains "data about cell tower locations in Kenya showing different signals e.g. CDMA, LTE, GSM" and the area covered by each cell tower location. It was made available through the efforts of Humanitarian OpenStreetMap Team and was made available on the Humanitarian Data Exchange. It was last updated on Feb 14, 2019. [Source: Kenya Cell Tower Locations](https://data.humdata.org/dataset/kenya-cell-tower-locations)


#### Processed Data
**KEN_agesex_aggregated**
<br>

- This csv was created by processing all the .tif files under `raw/KEN_population_v2_0_agesex`.
- The processing involved creating a script that reads every .tif file, extracts the data from it (geospatial location and the population number under that age), converts the geospatial coordinates to an h3 hexagon using the Uber H3 library. We then generate different dataframes each representing a Raster file (.tif) utilizing the h3 hexagons IDs, which are then all merged together on the H3 ID, to produce this csv. If some coordinates overlap, they will be included in the same hexagon (and the sum of the population number will be used). 

**KEN_agesex_aggregated**
<br>

- This csv was created by processing all the .tif files under `raw/KEN_population_v2_0_agesex`.
- The processing involved creating a script that reads every .tif file, extracts the data from it (geospatial location and the population number under that age), converts the geospatial coordinates to an h3 hexagon using the Uber H3 library. We then generate different dataframes each representing a Raster file (.tif) utilizing the h3 hexagons IDs, which are then all merged together on the H3 ID, to produce this csv. If some coordinates overlap, they will be included in the same hexagon (and the sum of the population number will be used). 

**KEN_population_age_demographics_merged**
<br>

- This csv was created by merging `KEN_agesex_aggregated` and `raw/kontur_population_KE_20231101` to produce a comprehensive dataset that contains population number and the age demographics for each hexagon. 
- The strategy used to merge these datasets is based on extensive EDA. First, the number of hexagons with with age demographics is a lot higher than the number of hexagons with population data. We found out that the size not matching is purely due to a difference in data points (i.e the age demographics just has more data) and not due to datapoint overlapping. The age demographics data has a lot more hexagons (which I was able to see when I plotted both datasets in a map). Decided to perform an left join (joining population density into age demographics). The result had 181k matching records. The remaining 54k records that had a null value for the total_population were filled out by summing the data coming the age demographics (i.e total_population = total_male + total_female). The resulting dataframe has 0 missing values. 
- Please note that the dataframe has a column called population_difference, which refers to the discrepancy in the population number between both datasets. A positive value indicates that the population number reported in `raw/kontur_population_KE_20231101` is higher than the one reported in `KEN_agesex_aggregated` (after summing total_male and total_female, two columns I created). A negative value means the opposite. This column was included to prevent any information loss. 

**KEN_h3_data_full**
<br>

- This dataset contains the final result of augmenting all the h3 hexagons with relevant data. This includes age demographics, population density, county, sub-county, MPI data (poverty, which is only focused on the sub-county level. More granular data was not found), and crime data (whether the hexagon belongs to a sub-county that has a high crime rate compared to the other sub-counties within the same county).

**Data Extracted From Points of Interests (POIs)**
<br>

- As mentioned above, the points of interests dataset was used to extract data that represent different "segments" or "categories. Through our EDA and cross-referencing the data with other sources on the internet, I believe that the data is not an exhaustive list of all points of interests, but it still provides a good overview and could help paint a better picture of their distribution in Kenya. For a more extensive overview of what each file includes exactly, please look into the script `src/process_points_of_interest.py`, where each function is responsible for creating one csv. List of csvs extracted:
- *KEN_agr_env_points*: contains data about points of interest relating to environmental and agriculture data, which includes but is not limited to 'grinding_mill', 'compost_site','water_or_irrigation', 'water_point', 'watering_place'.
- *KEN_educational_facilities_points*: contains data about points of interest relating to educational facilities. 
- *KEN_food_beverage_points*: contains data about points of interest relating to locations providing food and beverage, such as 'restaurant', 'bar' etc..
- *KEN_health_facilities_points*: contains data about points of interest relating to health facilities such as 'hospitals', 'dispensaries', 'pharmacies', 'clinics' etc..
- *KEN_leisure_points*: contains data about points of interest relating to leisure facilities such as 'cinema', 'casino' etc..
- *KEN_public_amenities_points*: contains data about points of interest relating to public amenities such as 'waste_disposal', 'waste_transfer_station', 'waste_basket', 'sanitary_dump_station' etc..
- *KEN_public_services_points*: contains data about points of interest relating to public services  such as 'police station', 'emergency services', 'fire stations' etc..
- *KEN_religious_buildings_points*: contains data about points of interest relating to religious buildings such churches and mosques. It is important to note that most data points are identified as 'place_of_worship', which can indicate any form of religious building, making the different classes in the 'amenity' column nuanced. 
- *KEN_shopping_retail_points*: contains data about points of interest relating to shopping and retail amenities such shops, marketplaces, and supermarkets. 
- *KEN_transportation_points*: contains data about poitns of interest relating to transportation amenities such as bus stops and train stations. 

**Crimes Data By Sub-county**
<br>

- The dataset with crime data was constructed from the report titled ["PRELIMINARY REPORT ON 2022 NATIONAL CRIME MAPPING: PUBLIC PERCEPTIONS AND EXPERIENCES OF CRIME PREVALENCE IN KENYA"](https://www.crimeresearch.go.ke/wp-content/uploads/2023/06/Preliminary-Report-on-2022-National-Crime-Mapping.pdf). "The study is a national survey conducted in all the 47 counties of Kenya. It focus on:
identifying the prevalence and types of crime; Country specific type and prevalence of
crimes, hotspot areas, criminal gangs and activities in which they are involved; root causes of
crime; predisposing factors to crimes; existing crime prevention measures, and policy
recommendations". The report was published by the Kenyan National Crime Research Center, a state corporation under The Ministry of Interior and National Administration. The dataset found under `processed/KEN_MPI_COUNTY_PROCESSED.csv` was created by extracting the data from the appendix on page 102, 'Crime Hotspot Areas and Names of Criminal gangs in Counties & Sub-Counties'. Since the PDF formatting was not consistent, the dataset was created manually by copying the data to csv. Note: this dataset might be updated soon since it doesn't contain all the data from the report.  


### How much data will be needed (Power Analysis)
Uber H3 Hexagons have different resolutions, each covering a different surface area. In my
case, I will be focusing on resolution 8, where the average hexagon area is about 0.74 km^2.
Given the area that each hexagon covers, we can calculate the number of hexagons we will
be using (or observations), given that we know Africa’s surface area: (11,724,000/0.73732) =
15,900,830 hexagons (or observations). To cover Kenya’s surface area, we will need
(582,646/0.73732) = 790,221 hexagons. I am expecting some of these observations to have
missing data for some of the features, depending on the datasets available. However, given
that the WorldPop’s dataset includes population data at 1km resolution, I am expecting the
population and age demographics features to be almost complete, meaning I’d have around
790,221 hexagons that carry population data, which should allow for interesting map
visualizations and the uncovering of interesting insights. 

### Data Collection
The data collection is based on the following protocol:
1. Search for data that could be used as proxy for affluency score or that can provide better insights about the socio-economic state of Kenya 
2. If the data is extensive enough, augment the h3 hexagons with that data. 
3. If not, process the data separately and extract the relevant information. Processing includes but is not limited to filling null values using different techniques and dropping column with mostly null values
4. Merge any dataset that require merging (such as the h3 hexagons if different datasets contain different data that could be used to augment the H3 hexagons). 

## Exploratory Data Analysis


## Ethics Statement

The dataset adheres to strict ethical guidelines, ensuring that no personal identifiable information (PII) is included. All data sources have been evaluated for ethical sourcing practices, and the dataset aims to mitigate potential biases by including diverse metrics. Efforts have been made to ensure transparency and inclusivity, preventing misuse or discriminatory applications.

## How To Access The Dataset
[Link To The Dataset](https://huggingface.co/datasets/ahmedboutar/kenya-mapping-for-economic-development)


### License
This dataset is licensed under the Creative Commons Attribution 4.0 International License (CC-BY 4.0). 

To view a copy of this license, visit http://creativecommons.org/licenses/by/4.0/

If you use this dataset, please cite:
Dataset created by Ahmed Boutar (2024). Available at: https://huggingface.co/datasets/ahmedboutar/kenya-mapping-for-economic-development