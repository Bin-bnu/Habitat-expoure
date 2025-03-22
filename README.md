How do land use change and heat exposure affect the future habitat suitable range of endangered species?
Project Overview
This project analyzes the impact of land use change and heat exposure on the future suitable habitat range of endangered species. A series of Python scripts are used to process, analyze, and visualize habitat changes at different scales (global, national, and continental).

File Descriptions
0Heat exposure was tailored by species.py
Extracts heat exposure data for each species, ensuring that the heat exposure analysis is specific to their actual habitat range.

1The heat of each species habitat is divided into 8 categories.py
Classifies the habitat heat exposure into 8 different levels, allowing for detailed statistical analysis.

2Statistical information on habitat changes of species.py
Computes habitat area changes for each species, assessing the impact of land use change on habitat loss or expansion.

3The single species scale was further used to calculate the changes in species numbers.py
Analyzes species population changes at the individual species level, identifying trends in habitat suitability under future climate conditions.

4Habitat area by continent.py
Calculates and compares the habitat area by continent, evaluating how different regions are affected by land use and climate change.

5The heat exposure area of 8 types of different species was calculated.py
Computes heat exposure areas for 8 different species groups, assessing their vulnerability to heat stress.

6The area of loss area was analyzed by continent.py
Analyzes habitat loss by continent, identifying geographic trends in species habitat reduction.

7Statistical changes in heat exposure by country.py
Examines changes in heat exposure at the national level, assessing the potential threats faced by species in different countries.

8Statistical global scale eight fall species scale.py
Conducts a global-scale analysis of the 8 endangered species groups, evaluating biodiversity risks worldwide.

9Longitude and latitude histogram statistics.py
Generates histograms of species habitat distribution by latitude and longitude, providing insights into geographic trends.

Requirements
Python 3.x

Required libraries:

bash
pip install numpy pandas geopandas rasterio matplotlib tqdm
Usage
Run the scripts in sequence to complete the data processing and analysis.


Output
Statistical results will be saved as CSV files.

Visualizations (e.g., maps, histograms) will be saved as PNG or PDF files.

The output file formats and locations can be adjusted within each script.

References
This study integrates data on land use change, biodiversity, and climate impact modeling to assess future habitat suitability for endangered species. It follows the latest ecological and climate modeling research.
