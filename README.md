# Mapping for Economic Development (KENYA)

## Project Overview
This project aims to curate and open source a novel dataset aimed at fostering
economic development in Africa, with an initial focus on Kenya. The dataset will combine
various geographical and demographic data to enable businesses, researchers, and possibly lawmakers to make better informed decisions, conduct valuable analyses, and have a better understanding and overview of the geographical area of their choosing.
This project curates and open sources a novel dataset designed to foster economic development in Africa, starting with Kenya. By combining geospatial and demographic data, this dataset's goal is to enable businesses, researchers, and policymakers to make data-driven decisions, conduct meaningful analyses, and gain detailed insights into specific geographical areas (all relevant data in one place).

## Folder Structure

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


### Scripts contents 

- `aggregate_age_demographics.py`: This script processes the files in the folder `raw/KEN_population_v2_0_agesex`. It loads all the .tif files, extracts the data corresponding to each age range along with the coordinates (which it converts to a different map projection if needed) and creates a column with the h3 indices. Once all the files have been processed, it outputs a csv with all the data merged on the h3 IDs. The output csv will have a list of h3 hexagons with the age demographics (number of males/females under specific age), named `aggregate_age_demographics.py`.
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
The data collected comes from different sources, serve different purposes, and have been utilized in different ways:
| Dataset | Data type | Source | Provenance | Description|
|----------|----------|----------|----------|----------|
| Row 1-1  | Row 1-2  | Row 1-3  | Row 1-4  |  Row 1-4 |
| Row 2-1  | Row 2-2  | Row 2-3  | Row 2-4  |  Row 1-4 |
| Row 3-1  | Row 3-2  | https://data.humdata.org/dataset/hotosm_ken_financial_services | Row 3-4  |  Row 1-4 |

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

### Data Collection (before overlaying the data with the h3 hexagons)
1. Generate H3 hexagons overlaying the chosen geographical locations using the open-
source H3 library (Source: H3 library for hexagon generation)
2. Collect population data and age demographics from WorldPop, which allows us to see
population data at a 1km resolution (E.g. https://hub.worldpop.org/geodata/listing?id=75)
3. Gather building footprint from the GlobalMLBuildingFootprints, which allows us to see the
building footprints at (Source for Kenya’s dataset: KenyaNigeriaBuildingFootprints)
5. Potentially incorporate additional relevant data as the project progresses (and as I find
relevant datasets from trusted sources) (e.g. world soil database)

## Exploratory Data Analysis



## Ethics Statement

The dataset adheres to strict ethical guidelines, ensuring that no personal identifiable information (PII) is included. All data sources have been evaluated for ethical sourcing practices, and the dataset aims to mitigate potential biases by including diverse metrics. Efforts have been made to ensure transparency and inclusivity, preventing misuse or discriminatory applications.

## How To Access The Dataset
[Link To The Dataset](https://huggingface.co/datasets/ahmedboutar/kenya-mapping-for-economic-development)


### License
This dataset is licensed under the Creative Commons Attribution 4.0 International License (CC-BY 4.0). 
---
license: cc-by-4.0
---

To view a copy of this license, visit http://creativecommons.org/licenses/by/4.0/

If you use this dataset, please cite:
Dataset created by Ahmed Boutar (2024). Available at: https://huggingface.co/datasets/ahmedboutar/kenya-mapping-for-economic-development