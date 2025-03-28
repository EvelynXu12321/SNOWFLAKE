import streamlit as st
import folium
import pandas as pd
import os
from streamlit_folium import st_folium
import json

# Set page configuration
st.set_page_config(layout="wide", page_title="SVI & EAL Map of Florida", page_icon="🌎")

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #333333;  /* Dark gray background for contrast */
    }
    .title, .description, .map-title {
        text-align: center;
        color: #ffffff;  /* Set text color to white */
    }
    .title {
        font-size: 2.5em;
        margin-bottom: 0.5em;
    }
    .description {
        font-size: 1.2em;
        margin-bottom: 1em;
    }
    .sidebar .sidebar-content {
        background-color: #444444;  /* Slightly lighter gray for sidebar */
    }
    .map-title {
        font-size: 1.5em;
        margin-top: 1em;
    }
    .faq {
        background-color: #555555;
        padding: 20px;
        border-radius: 10px;
        margin: 20px auto;
        max-width: 600px;  /* Smaller width for FAQ box */
        color: #ffffff;
    }
    .faq h3 {
        text-align: center;
        margin-bottom: 5px;
    }
    .faq p {
        text-align: justify;
        line-height: 1.6;
        margin: 20px;  /* Larger margins for text */
    }
    </style>
    """, unsafe_allow_html=True)

# Page title and description
st.markdown("<div class='title'>Social Vulnerability Index & Expected Annual Loss: Map of Florida</div>", unsafe_allow_html=True)
st.markdown("<div class='description'>Data Source: CDC/ATSDR, FGIO, FEMA</div>", unsafe_allow_html=True)
st.markdown("<div class='description'>Explore the social vulnerability and expected annual loss due to hurricanes in Florida.</div>", unsafe_allow_html=True)

# Load GeoJSON data
county = os.path.join('USA_Counties_(Generalized).geojson')
with open(county) as f:
    county_geojson = json.load(f)

# Filter GeoJSON to include only features for Florida
florida_geojson = {
    "type": "FeatureCollection",
    "features": [
        feature for feature in county_geojson["features"]
        if feature.get("properties") and feature["properties"].get("STATE_NAME") == "Florida"
    ]
}

# Sidebar customization
st.sidebar.title("Filters")

# Add visualization type selection
visualization_type = st.sidebar.radio(
    "Select Visualization Type:",
    ('Social Vulnerability Index', 'Expected Annual Loss')
)

# Define display names and map them to actual column names in your dataset
svi_column_map = {
    'Socioeconomic Status': 'RPL_THEME1',
    'Household Characteristics': 'RPL_THEME2',
    'Racial & Ethnic Minority Status': 'RPL_THEME3',
    'Housing Type & Transportation': 'RPL_THEME4',
    'Overall': 'RPL_THEMES'
}

eal_column_map = {
    'Total': 'HRCN_EALT',
    'Building': 'HRCN_EALB',
    'Population Equivalence': 'HRCN_EALPE',
    'Agriculture': 'HRCN_EALA'
}

# Define color mappings for each choropleth type
color_map = {
    'Socioeconomic Status': 'YlOrRd',
    'Household Characteristics': 'BuGn',
    'Racial & Ethnic Minority Status': 'PuBu',
    'Housing Type & Transportation': 'OrRd',
    'Overall': 'Purples',
    'Total': 'YlGnBu',
    'Building': 'YlOrBr',
    'Population Equivalence': 'YlGn',
    'Agriculture': 'YlOrRd'
}

# Load data
if visualization_type == 'Social Vulnerability Index':
    # Add comparison scope selection for SVI
    comparison_scope = st.sidebar.radio(
        "Select Comparison Scope:",
        ('Florida', 'United States')
    )
    
    selected_option = st.sidebar.selectbox(
        "Select a Category:",
        list(svi_column_map.keys()),
        index=list(svi_column_map.keys()).index('Overall')  # Set default to 'Overall'
    ).strip()
    column_name = svi_column_map[selected_option]
    
    # Load data based on the selected comparison scope
    if comparison_scope == 'Florida':
        data_file = 'Florida_county.csv'
    else:
        data_file = 'SVI_2022_US_county.csv'
else:
    selected_option = st.sidebar.selectbox(
        "Select a Consequence Type:",
        list(eal_column_map.keys())
    ).strip()
    column_name = eal_column_map[selected_option]
    data_file = 'NRI_Table_Counties_Florida.csv'

color = color_map[selected_option]

# Correct the file path for the US data
data = os.path.join(data_file)
svi_data = pd.read_csv(data)
svi_data['COUNTY'] = svi_data['COUNTY'].str.replace(r'\s*County', '', regex=True)

# Convert EAL values to thousands if EAL is selected
if visualization_type == 'Expected Annual Loss':
    svi_data[column_name] = svi_data[column_name] / 1000

# Use the same GeoJSON data for both scopes to only show Florida
geojson_data = florida_geojson
key_on = 'feature.properties.NAME'

# Center the map on Florida for both scopes
location = [27.5, -82]  # Centered on Florida
zoom_start = 7

# Create the map with Folium
m = folium.Map(location=location, zoom_start=zoom_start, tiles='cartodbpositron')

# Create the choropleth layer
choropleth = folium.Choropleth(
    geo_data=geojson_data,
    name=selected_option,
    data=svi_data,
    columns=['COUNTY', column_name],
    key_on=key_on,
    fill_color=color,
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name=f'{selected_option} Rate'
).add_to(m)

# Add tooltips to the map
for feature in geojson_data['features']:
    county_name = feature['properties']['NAME']
    population = feature['properties'].get('POPULATION', 'N/A')
    spl_value = svi_data.loc[svi_data['COUNTY'] == county_name, column_name].values
    spl_value_text = f"{selected_option}: {spl_value[0]:,.1f}K" if len(spl_value) > 0 else f"{selected_option}: N/A"

    folium.GeoJson(
        feature['geometry'],
        line_opacity=0,
        tooltip=folium.Tooltip(f"County: {county_name}<br>Population: {population}<br>{spl_value_text}"),
        style_function=lambda x: {'color': 'transparent'}
    ).add_to(m)

# Display the map in Streamlit
st.markdown(f"<div class='map-title'>Choropleth Map for {selected_option} ({visualization_type})</div>", unsafe_allow_html=True)

# Center the map on the page using columns
col1, col2, col3 = st.columns([1, 6, 1])  # Adjust center width with ratios
with col2:
    st_folium(m, width=1000, height=700)  # Set map size back to previous dimensions

# Display FAQ section only when Social Vulnerability Index is selected
if visualization_type == 'Social Vulnerability Index':
    st.markdown("<div class='faq'><h3>Frequently Asked Questions</h3>", unsafe_allow_html=True)
    st.markdown("""
    <p><strong>What is Social Vulnerability?</strong><br>
    Social vulnerability refers to demographic and socioeconomic factors that contribute to communities being more adversely affected by public health emergencies.</p>

    <p><strong>How do I interpret the CDC/ATSDR SVI ranking for a county?</strong><br>
    A percentile ranking represents the proportion of counties that are equal to or lower than a county of interest in terms of social vulnerability. For example, an SVI ranking of 0.85 signifies that 85% of counties in the state or nation are less vulnerable than the county of interest and that 15% of counties in the state or nation are more vulnerable.</p>

    <p><strong>What is the difference between the U.S.-based and state-based CDC/ATSDR SVI databases?</strong><br>
    The U.S.-based SVI database compares the social vulnerability of a county to all counties in the United States. The state-based SVI database compares the social vulnerability of a county solely to counties within a particular state of interest.</p>

    <p>For further information, please visit <a href="https://www.atsdr.cdc.gov/place-health/php/svi/svi-data-documentation-download.html" style="color: #00c0f2;">CDC/ATSDR SVI Data Documentation</a></p>
    </div>
    """, unsafe_allow_html=True)