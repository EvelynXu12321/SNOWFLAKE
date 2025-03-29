# Building Resilience in Coastal Communities During Hurricanes, Snowflake
## Fall 2024, AI Studio Project

# Table of Contents

1. [Project Overview](#project-overview)
2. [Objectives](#objectives)
3. [Goals](#goals)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Data Preparation and Validation](#data-preparation-and-validation)
7. [Approach](#approach)
8. [Key Findings and Insights](#key-findings-and-insights)
9. [Acknowledgements](#acknowledgements)


## Project Overview
Hurricanes, such as Helene and Milton in Florida, have shown how devastating these natural disasters can be for coastal communities. Damaged infrastructure, flooded buildings, and limited access to essential services like healthcare, clean water, and food pose significant challenges during and after hurricanes. Vulnerable populations face long-term consequences, including economic losses, mental health struggles, and prolonged displacement. Social, cultural, economic, and geographic barriers further exacerbate healthcare delivery and access disparities, leaving these communities even more vulnerable.

## Objectives
This project aims to address these challenges by developing a model that assesses risk scores based on various factors and create an interactive tool that is easy for health intervention groups and individuals to navigate. This tool will help optimize resource allocation, visualize the communities most in need, and provide actionable insights for disaster preparedness and response.

The tool empowers health groups to proactively allocate resources where they are needed most. It also informs individuals about social determinants and risks specific to their location, enabling better evacuation and preparation decisions. Ultimately, the goal is to equip underrepresented coastal communities with data-driven insights for improved resilience.

## Goals
To achieve this, we utilized datasets highlighting social determinants of health, including the Social Vulnerability Index (SVI) and the National Risk Index. These datasets track factors such as income, education, healthcare access, transportation, hurricane paths, and proximity to essential services. By combining social and geographic data, the model identifies key risks and correlations to inform disaster preparedness strategies.

While hurricanes are unavoidable, their impacts can be mitigated by addressing social vulnerabilities before disaster strikes. Our project focuses on reducing post-disaster losses and improving resilience in coastal communities through proactive, informed preparation.

## Installation

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run Info.py
   ```

## Usage

<img src="/figures/usage.png" alt="Alt text" width="700">
<p><em>Figure 1: Sidebar filter and address input interface</em></p>

<img src="/figures/usage_2.png" alt="Alt text" width="700">
<p><em>Figure 2: Tooltip functionality for hurricane paths and critical facilities</em></p>


1. Use the sidebar filter on the left (refer to Figure 1) to:
   -  Select variables to display on the map.
   -  View colored markers representing critical facilities and their hurricane risk severity.
   -  See hurricane paths as colored lines, with key events marked as red dots.
2. Enter an address to receive a personalized risk score (refer to Figure 1):
   - The score is calculated using our custom machine learning algorithm.
   - It incorporates geospatial insights such as proximity to hurricane paths and frequency of hurricane intersections.
   - It also includes social insights from the Social Vulnerability Index (SVI).
3. Use the tooltips for detailed information (refer to Figure 2):
   - Hover over a hurricane path to see metrics like the hurricane’s name, type of sequential disaster, wind speed, and pressure.
   - Hover over a critical facility to view its name, type, and calculated risk score.

## Data Preparation and Validation

### DATASET DESCRIPTION
Our project utilized a range of datasets to assess and mitigate risks, each providing unique insights and complementary information for understanding vulnerabilities in Florida’s coastal communities.

**FEMA National Risk Index (NRI)**: The NRI dataset assesses risks from 18 natural hazards, including hurricanes, floods, and wildfires, integrating hazard, exposure data, and vulnerability factors. It calculates risk scores and expected annual losses to guide decision-making for disaster preparedness and resilience. The dataset, available in the Snowflake Marketplace (update 1.19.0 as of 3/23/2023) and has been used in our development of the second model, identifying at-risk communities, and helping to prioritize resources.

**CDC Social Vulnerability Index (SVI)**: The SVI highlights socioeconomic and demographic indicators at the census-tract level, helping identify populations most vulnerable to disasters. This dataset is used in both the second model development and the interactive tool, helping to identify areas where intervention is most needed and enabling targeted disaster preparedness.

**Diversity, Equity, and Inclusion – Social Determinants of Health**: This dataset, available in the Snowflake Marketplace, was used for exploratory data analysis. It provided valuable insights into social determinants like income, education, and healthcare access, highlighting disparities that influence disaster impact and recovery.

**Critical Facilities in Florida (Overpass Turbo)**: Using Overpass Turbo, a web-based data mining tool for OpenStreetMap, we sourced location data for critical facilities like hospitals, clinics, and shelters. The data was parsed from JSON and formatted into a CSV for use in the interactive tool, providing information on the geographic distribution of essential services during disasters.

**Hurricane Paths (HURDAT2)**: Historical hurricane path data from the National Hurricane Center was processed from text files into a usable format, including detailed updates every six hours. These data points allowed us to map precise hurricane paths, which were integrated into the interactive tool to visualize historical patterns and inform preparedness.

### EDA (EXPLORATORY DATA ANALYSIS)
The purpose of EDA in our project was to uncover relationships within the Diversity, Equity, and Inclusion dataset, focusing on how socioeconomic factors influence community outcomes. We began by summarizing the key variables, checking for missing data, and resolving inconsistencies to ensure reliable analysis. To explore the data, we used visualization like scatter plots, box plots, and histograms, which provided insights into individual variables and their interrelationships.

While we created many visualizations during the process, two stood out as the most meaningful for our analysis.

<img src="/figures/figure_1.png" alt="Alt text" width="400">
<p><em>Figure 3: Income, Healthcare Access, and Housing Affordability</em></p>

This visualization examines the relationship between median household income, healthcare access (measured by the uninsured rate), and housing affordability in Florida. It highlights an inverse relationship between income and the uninsured rate, where higher-income areas typically have fewer uninsured individuals. Additionally, there is a strong link between rent burden and healthcare access; areas with higher percentages of households spending more than 30% of their income on rent tend to have higher uninsured rates. Since we have geospatial data in the dataset, we can identify areas where low-income households face high uninsured rates and significant rent burdens, which allows us to pinpoint communities that may be particularly vulnerable to healthcare disruptions during a hurricane.

<img src="/figures/figure_2.png" alt="Alt text" width="400">
<p><em>Figure 4: Public Health Insurance Coverage Distribution</em></p>

This visualization compares the distribution of public health insurance types in Florida. Medicaid coverage stands out with the highest median and widest range, indicating it supports a larger portion of the population. In contrast, the “other public insurance” category shows the lowest median and range, reflecting more limited coverage. TRICARE/VA Only and Medicare Only have lower, more consistent median values, indicating less limited accessibly among the broader population. 

Understanding the distribution of public health insurance types helps the AI tools assess which communities have stronger healthcare support networks. These insights can guide decisions on resources allocation and preparedness, ensuring healthcare needs are met during and after a hurricane.


### FEATURE SELECTION

**First Model (Web-Interactive Tool)**: The first model focuses on predicting a precomputed risk score for each building in Florida, considering its vulnerability to hurricanes. Feature engineering was a key step in ensuring the model captured meaningful patterns in data.

**Features Engineered**:
1. **Proximity to Coastline**: Using Florida's coastline shapefiles, we calculated the minimum distance from each location to the coast. This metric reflects the likelihood of a building being impacted by storm surges and coastal flooding.
2. **Historical Hurricane Intersections**: Leveraging historical hurricane path data, we calculated how many times a building’s location intersected with a hurricane path. A buffer radius of 50 kilometers was applied to the hurricane paths to account for the area of impact beyond the path itself. Locations within this buffer were considered intersected.
3. **Social Vulnerability Index (SVI)**: Each location was assigned the SVI score of its corresponding census tract. This score accounts for socioeconomic factors, such as income and education, that influence a community’s ability to prepare for and recover from disasters.

**Label Engineering**: The label for this model was a precomputed risk score derived from the minimum haversine distance of each location to historical hurricane paths. This metric provides a straightforward way to quantify hurricane risk.

**Second Model (Risk Prediction)**: The second model development aimed to assess risk using a more comprehensive dataset with 223 features. To prevent overfitting and improve predictive accuracy, we implemented a structured feature selection process and defined the **FEMA Risk Score (F_TOTAL)** as the prediction label.

**Feature Selection Process:**
1. **Correlation Matrix Analysis**: We calculated the correlation between features and the target variable, identifying the most influential predictors. Highly correlated features were prioritized for inclusion, while redundant or weakly correlated features were removed to avoid overfitting.
2. **Dimensionality Reduction**: Reducing the dimensionality of the dataset ensured the model remained computationally efficient.
3. **Exhaustive Search for Best Parameter**: An exhaustive search was conducted to identify the optimal parameters for an ensemble regressor. This helped balance the trade-off between model complexity and predictive power.

**Key Features Selected:**
- **SVI Socioeconomic Status**: Strong relationship (0.679) with the target variable, capturing economic vulnerabilities.
- **SVI Household Composition and Disability**: Moderate correlationship (0.215), reflecting household-level risks.
- **Household with No Vehicles**: Correlation of 0.045, representing transportation limitation during evacuations.
- **Housing Structure with 10+ Units**: Correlations of 0.017 and 0.015, indicating structural vulnerability.

These features collectively accounted for approximately 80% of the total correlation, providing a focused dataset for model training. 



## Approach
### SELECTED MODELS
For the web-interactive tool, we selected a Random Forest model due to its robustness, particularly when working with datasets derived from geographical and environmental metrics that often include inherent variability. Random Forest is well-suited for handling smaller datasets, typically ranging from a few hundred to thousands of data points, while maintaining strong predictive power. Its ability to handle non-linear relationships and provide accurate predictions made it an ideal choice for this project.

The second focused on aiding healthcare providers and disaster response teams by identifying the most vulnerable regions and offering case-specific solutions. To achieve this, we explained both Random Forest Regressor, Stochastic Gradient Boosting Trees (SGBT) Regressor due to their complementary strengths.
- **Random Forest Regressor**: Independent and Parallel processing, providing robust and stable predictions, particularly effective for non-linear data relationships.
- **SGBT Regressor**: Sequential and self-correcting, refining prediction iteratively to minimize errors and improve accuracy.

Both models were trained using supervised learning techniques on datasets such as the Social Vulnerability Index (SVI) and National Risk Index (NRI). Evaluation metrics, including R-squared, Root Mean Squared Error (RMSE), and Mean Error, were used to assess performance and fine-tune parameters. Ensemble learning techniques were applied to extract precise predictions, ensuring the model’s outputs were actionable and reliable.


## Key Findings and Insights

<p align="center">
  <img src="/figures/residual_1.png" alt="First Model's Residual Analysis" width="400">
  <img src="/figures/residual_2.png" alt="Second Model's Residual Analysis" width="400">
</p>
<p align="center">
  <em>Figure 5: First Model's Residual Analysis &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; Figure 6: Second Model's Residual Analysis</em>
</p>

### First Model: Performance and Insights
- **Mean Squared Error (MSE)**: The model achieved a low MSE of 0.006, indicating that on average, predictions were close to actual values. This highlights the model’s ability to make accurate predictions overall.
- **R-squared Score**: The model explained 20% of the variation in the data, which shows that while it provides some explanation for the outcomes, there is substantial variability that remains unaccounted for.
- **Residual Analysis** (Refer to Figure 5):
   - The residuals were mostly small and close to zero, consistent with the low MSE, confirming general accuracy in predictions.
   - However, residuals showed some patterns, particularly at higher predicted values where they tended to spread out more. This suggests the model struggles with variability in this range, limiting the R-squared score.
- **Future Improvements**: Additional feature engineering and expanding the dataset would likely enhance the model’s ability to capture variability and improve overall performance.

### Second Model: Refinement and Performance
#### Random Forest Model
- The training RMSE of 1.86 showed good model fit, but testing RMSE increased to 3.22, reflecting potential overfitting.
- Cross-validation RMSE values ranged from 0.63 to 5.43 in earlier iterations, stabilizing at 1.73 with refinements, indicating improved consistency.

#### Gradient Boosted Decision Tree (GBDT)
- The model achieved a low test RMSE of 0.37 (log-transformed), demonstrating strong prediction accuracy.
- Adjusted MAPE of 20.61% further confirmed reasonable performance with log-transformed data.
- **Residual Analysis** (Refer to Figure 6):
   - Residuals were scattered evenly around zero, with smaller residuals for higher true values, indicating consistency in predictions.
   - The histogram of residuals showed a strong peak near zero, confirming accuracy for most predictions.
   - The predicted vs. true values plot showed points closely aligning with the red line, suggesting robust agreement between predictions and actual values.
- Minor areas for improvement included slight asymmetry in residuals and occasional scatter, indicating opportunities for better handling of specific cases.


## Acknowledgements

This project would not have been possible without the support and contributions of many individuals and tools. We would like to express our gratitude to the Break Through Tech AI studio program at UCLA for providing the opportunity and resources to bring this project to life. Special thanks to our Challenge Advisor, [Joe Warbington](https://www.linkedin.com/in/warbington) from Snowflake, for his guidance and expertise throughout the project. 

Our dedicated team – [Ella Chung (UCI)](https://www.linkedin.com/in/ella-lynn-chung/), [Eric Lu (UCLA)](https://www.linkedin.com/in/ericslu/), [Evelyn Xu (UCLA)](https://www.linkedin.com/in/evelyn-xu-ucla/), [Prachi Heda (UCSD)](https://www.linkedin.com/in/prachi-heda-bb281720b/), and [Kaleo Cao (UCSD)](https://www.linkedin.com/in/cyc2025/) – worked collaboratively to achieve our goals and deliver meaningful outcomes.

We want to give a shout out to the tools and libraries that were essential to making this project happen, including Snowflake, scikit-learn (Snowflake.ml.modeling library), SQL, Streamlit, Snowflake Marketplace, and Snowflake Notebook, which provided the technical foundation for our analyses and interactive tools.

Thank you to everyone who contributed to this project's success.
