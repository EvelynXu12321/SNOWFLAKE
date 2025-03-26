import streamlit as st
import pandas as pd
import folium
import os
import json
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import branca.colormap as bcm
from folium import CircleMarker, PolyLine
import requests
import geopandas as gpd
import joblib
from shapely.geometry import Point

st.set_page_config(layout="wide")

@st.cache_data
def load_florida_gdf_geojson():
    # Load GeoJSON directly as GeoDataFrame
    return gpd.read_file('florida_gdf.geojson')


@st.cache_data
def load_coastline_data():
    coastline_gdf = gpd.read_file('Florida_Shoreline.shp')

    # If the CRS is not detected, set it manually
    if coastline_gdf.crs is None:
        coastline_gdf.set_crs('EPSG:4326', inplace=True)  # Assuming it's in WGS84 (Latitude/Longitude)

    # Now convert to Florida's CRS
    return coastline_gdf.to_crs('EPSG:3086')

@st.cache_data
def load_hurricane_data():
    hurricane_data = pd.read_csv('HURDAT2_hurricane_data_with_events.csv')
    hurricane_gdf = gpd.GeoDataFrame(
        hurricane_data,
        geometry=gpd.points_from_xy(hurricane_data.longitude, hurricane_data.latitude),
        crs='EPSG:4326'
    )
    hurricane_gdf = hurricane_gdf.to_crs('EPSG:3086')  # Project to Florida's CRS
    hurricane_gdf['geometry'] = hurricane_gdf.buffer(50000)  # Buffer by 50 km
    return hurricane_gdf

@st.cache_resource
def load_model():
    return joblib.load('risk_prediction_model_best.pkl')

# Load data and model
florida_gdf = load_florida_gdf_geojson()
coastline_projected = load_coastline_data()
hurricane_gdf_projected = load_hurricane_data()
model = load_model()


# Load county GeoJSON data
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

# Load SVI data
data_county = os.path.join('Florida_county.csv')
svi_county_data = pd.read_csv(data_county)
svi_county_data['COUNTY'] = svi_county_data['COUNTY'].str.replace(r'\s*County', '', regex=True)

# Load facilities data
facilities_df = pd.read_csv('facilities_with_risk_scores.csv')

# Ensure latitude and longitude are numeric
facilities_df['latitude'] = pd.to_numeric(facilities_df['latitude'], errors='coerce')
facilities_df['longitude'] = pd.to_numeric(facilities_df['longitude'], errors='coerce')

# Drop facilities with missing coordinates
facilities_df = facilities_df.dropna(subset=['latitude', 'longitude'])

# Load hurricane data
hurricane_data = pd.read_csv('HURDAT2_hurricane_data_with_events.csv')

last_10_hurricanes = [
    'IAN', 'ELSA', 'ETA', 'SALLY', 'DORIAN',
    'MICHAEL', 'IRMA', 'HERMINE', 'MATTHEW', 'ARTHUR'
]

# Filter hurricane data based on the last 10 hurricanes
filtered_hurricane_data = hurricane_data[hurricane_data['storm_name'].isin(last_10_hurricanes)]
hurricane_data = filtered_hurricane_data

# Set up Streamlit app
st.title("Florida Social Vulnerability Index, Facility Risk Map, and Hurricane Paths")

st.sidebar.title("Filters")

# Facility type filter
facility_types = facilities_df['type'].unique()
selected_types = st.sidebar.multiselect(
    'Select facility types to display:',
    facility_types,
    default=facility_types.tolist()
)

# Hurricane filter
# Get unique hurricane names
hurricane_names = hurricane_data['storm_name'].unique()
selected_hurricanes = st.sidebar.multiselect(
    'Select hurricanes to display:',
    hurricane_names,
    default=hurricane_names.tolist()
)

# Filter facilities based on selection
facilities_df_filtered = facilities_df[facilities_df['type'].isin(selected_types)]

# Normalize risk scores for coloring
risk_scores = facilities_df_filtered['risk_score']
norm = plt.Normalize(vmin=risk_scores.min(), vmax=risk_scores.max())
cmap = plt.get_cmap('YlOrRd')

# Initialize the map
m = folium.Map(location=[27.5, -82], zoom_start=6)

# User input for address
st.sidebar.subheader("Enter Address to Predict Risk Score")
address = st.sidebar.text_input("Address", placeholder="Enter a valid address in Florida")

if st.sidebar.button("Calculate Risk Score"):
    # We use Streamlit session state to persist errors across submissions
    if address:
        st.session_state['address'] = address
        st.session_state['submit_clicked'] = True

if 'submit_clicked' in st.session_state and st.session_state['submit_clicked']:
    converted_address = st.session_state['address'].strip().replace(" ", "+")
    url = f"https://nominatim.openstreetmap.org/search?q={converted_address}&format=json"
    headers = {"User-Agent": "streamlitapp/1.0"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if not data:
            st.error("Could not geocode the address. Please try a different one.")
        else:
            first = data[0]
            st.success(f"Address geocoded successfully: {first['display_name']}")
            user_point = Point(first['lon'], first['lat'])

            # Reproject the user point to the projected CRS
            user_geom = gpd.GeoDataFrame(
                geometry=[user_point], crs='EPSG:4326'
            ).to_crs('EPSG:3086')

            # Calculate distance to coastline
            user_geom_projected = user_geom.iloc[0].geometry
            distance_to_coast_km = coastline_projected.distance(user_geom_projected).min() / 1000

            # Calculate hurricane exposure using a spatial join
            user_buffered = user_geom.buffer(50000)  # Buffer by 50 km
            user_buffered_gdf = gpd.GeoDataFrame(geometry=user_buffered, crs='EPSG:3086')
            hurricanes_exposed = gpd.sjoin(
                user_buffered_gdf, hurricane_gdf_projected, how="inner", predicate="intersects"
            )
            hurricane_exposure = hurricanes_exposed['storm_name'].nunique()

            # Get SVI score using a spatial join
            user_geom_reprojected = user_geom.to_crs(florida_gdf.crs)
            svi_match = gpd.sjoin(
                user_geom_reprojected, florida_gdf[['geometry', 'RPL_THEMES']], how="inner", predicate="intersects"
            )
            if svi_match.empty:
                st.error("No matching county found for the input address.")
                svi_score = 0  # Default or error value
            else:
                svi_score = svi_match['RPL_THEMES'].values[0]

            # Prepare features and make prediction
            features = pd.DataFrame({
                'distance_to_coast_km': [distance_to_coast_km],
                'hurricane_exposure': [hurricane_exposure],
                'RPL_THEMES': [svi_score]
            })
            predicted_risk_score = 0
            if np.isfinite(features.values).all():
                predicted_risk_score = model.predict(features)[0] + 0.5
            else:
                st.error("The feature values contain invalid entries. Please check the input data.")

            # Display the results
            st.sidebar.success(f"Predicted Risk Score: {predicted_risk_score:.2f}")

            # Add user location to the map
            folium.CircleMarker(
                location=[first['lat'], first['lon']],
                radius=8,
                color='blue',
                fill=True,
                fill_color='blue',
                fill_opacity=0.6,
                popup=f"<b>Predicted Risk Score:</b> {predicted_risk_score:.2f}"
            ).add_to(m)
            st_folium(m, width=800, height=600)
    except Exception as e:
        st.error(f"An error occurred during geocoding: {e}")

# if st.sidebar.button("Calculate Risk Score") and address:
#     try:
#         # Geocode the address
#         location = geolocator.geocode(address)
#         if not location:
#             st.error("Could not geocode the address. Please try a different one.")
#         else:
#             st.success(f"Address geocoded successfully: {location.address}")
#             user_point = Point(location.longitude, location.latitude)

#             # Calculate distance to coastline
#             user_geom = gpd.GeoSeries([user_point], crs='EPSG:4326').to_crs('EPSG:3086')
#             if coastline_projected.empty:
#                 st.error("No coastline data available.")
#             distance_to_coast_km = coastline_projected.distance(user_geom.iloc[0]).min() / 1000

#             # Calculate hurricane exposure
#             hurricane_exposure = hurricane_gdf_projected[
#                 hurricane_gdf_projected.contains(user_geom.iloc[0])
#             ]['storm_name'].nunique()
#             if hurricane_exposure == 0:
#                 st.warning("No hurricane exposure data found. Defaulting to 0.")
#                 hurricane_exposure = 0

#             # Get SVI score
#             user_geom = user_geom.to_crs(florida_gdf.crs)
#             matching_counties = florida_gdf[florida_gdf.contains(user_geom.iloc[0])]
#             if matching_counties.empty:
#                 st.error("No matching county found for the input address.")
#             svi_score = matching_counties['RPL_THEMES'].values[0]

#             # Prepare features and make prediction
#             features = pd.DataFrame({
#                 'distance_to_coast_km': [distance_to_coast_km],
#                 'hurricane_exposure': [hurricane_exposure],
#                 'RPL_THEMES': [svi_score]
#             })
#             predicted_risk_score = model.predict(features)[0] + 0.5

#             # Display the results
#             st.sidebar.success(f"Predicted Risk Score: {predicted_risk_score:.2f}")

#             # Add user location to the map
#             m = folium.Map(location=[location.latitude, location.longitude], zoom_start=10)
#             CircleMarker(
#                 location=[location.latitude, location.longitude],
#                 radius=8,
#                 color='blue',
#                 fill=True,
#                 fill_color='blue',
#                 fill_opacity=0.6,
#                 popup=f"<b>Predicted Risk Score:</b> {predicted_risk_score:.2f}"
#             ).add_to(m)
#             st_folium(m, width=800, height=600)

#     except Exception as e:
#         st.error(f"An error occurred: {e}")


# Add SVI Choropleth Layer
folium.Choropleth(
    geo_data=florida_geojson,
    name='SVI Choropleth',
    data=svi_county_data,
    columns=['COUNTY', 'RPL_THEMES'],  # Use the 'RPL_THEMES' column for overall SVI
    key_on='feature.properties.NAME',
    fill_color='YlGnBu',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='SVI Overall Score'
).add_to(m)

# Define color mappings for each building type
layer_map = {
    'pharmacy': '#DC143C',
    'fire_station': '#228B22',
    'fuel': '#4682B4',
    'hospital': '#DAA520',
    'police': '#008080',
    'shelter': '#FF8C00',
    'social_facility': '#C71585',
    'veterinary': '#483D8B',
    'water_point': '#191970',
    'clinic': '#BA55D3'
}

# Add facility markers to the map
for idx, row in facilities_df_filtered.iterrows():
    risk_score = row['risk_score']
    if pd.notnull(risk_score):
        # Use the normalized risk score to get a color
        color = mcolors.rgb2hex(cmap(norm(risk_score)))
    else:
        # Use the color mapping based on facility type if risk score is missing
        color = layer_map.get(row['type'], '#000000')  # Default to black

    # Add a CircleMarker to the map
    CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=5,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=folium.Popup(
            f"<b>Name:</b> {row['name']}<br><b>Type:</b> {row['type']}<br><b>Risk Score:</b> {risk_score}",
            max_width=300
        )
    ).add_to(m)

hurricane_colors = {
    'IAN': '#FF0000',
    'ELSA': '#FFA500',
    'ETA': '#FFFF00',
    'SALLY': '#008000',
    'DORIAN': '#00FFFF',
    'MICHAEL': '#0000FF',
    'IRMA': '#800080',
    'HERMINE': '#FFC0CB',
    'MATTHEW': '#A52A2A',
    'ARTHUR': '#000000',
}

# Add hurricane paths to the map
for hurricane in selected_hurricanes:
    hurricane_df = filtered_hurricane_data[filtered_hurricane_data['storm_name'] == hurricane]
    coordinates = hurricane_df[['latitude', 'longitude']].values.tolist()
    color = hurricane_colors[hurricane]

    # Add the hurricane path as a PolyLine
    folium.PolyLine(
        locations=coordinates,
        color=color,
        weight=2,
        opacity=0.8,
        popup=f"Hurricane {hurricane}"
    ).add_to(m)

# Collect special events
special_events_df = filtered_hurricane_data[filtered_hurricane_data['event_label'].notnull()]

# Add special event markers
for idx, row in special_events_df.iterrows():
    event_label = row['event_label']
    wind_speed = row['max_wind']
    pressure = row['min_pressure']
    hurricane = row['storm_name']

    popup_content = (
        f"<b>Hurricane:</b> {hurricane}<br>"
        f"<b>Event:</b> {event_label}<br>"
        f"<b>Wind Speed:</b> {wind_speed} kt<br>"
        f"<b>Pressure:</b> {pressure} mb"
    )

    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=8,
        color='red',
        fill=True,
        fill_color='red',
        fill_opacity=0.9,
        popup=folium.Popup(popup_content, max_width=300)
    ).add_to(m)


# Create a linear color map for risk scores
colormap = bcm.LinearColormap(
    colors=[mcolors.rgb2hex(cmap(i)) for i in np.linspace(0, 1, 256)],
    vmin=risk_scores.min(),
    vmax=risk_scores.max(),
    caption='Facility Risk Score'
)
colormap.add_to(m)

# Add color key for facility types
legend_html = '''
     <div style="position: fixed; 
     bottom: 50px; left: 50px; width: 250px; height: 300px; 
     border:2px solid grey; z-index:9999; font-size:14px;
     background-color:white;
     ">
     &nbsp;<b>Facility Types Legend</b><br>
'''
for facility_type, color in layer_map.items():
    legend_html += f'&nbsp;<i style="background:{color};width:10px;height:10px;border-radius:50%;display:inline-block"></i>&nbsp;{facility_type}<br>'

legend_html += '</div>'
m.get_root().html.add_child(folium.Element(legend_html))

# Add hurricane legend
hurricane_legend_html = '''
     <div style="position: fixed; 
     bottom: 50px; right: 50px; width: 250px; height: 300px; 
     border:2px solid grey; z-index:9999; font-size:14px;
     background-color:white;
     ">
     &nbsp;<b>Hurricane Paths Legend</b><br>
'''
for hurricane, color in hurricane_colors.items():
    hurricane_legend_html += f'&nbsp;<i style="background:{color};width:10px;height:10px;display:inline-block"></i>&nbsp;{hurricane}<br>'

hurricane_legend_html += '</div>'
m.get_root().html.add_child(folium.Element(hurricane_legend_html))

# Display the map in Streamlit
st_folium(m, width=800, height=600)

# Additional content (optional)
st.markdown("""
    **How to interpret the map:**
    - The choropleth map shows the Social Vulnerability Index (SVI) of each county in Florida.
    - The colored markers represent critical facilities.
    - The color of each marker corresponds to the risk score of the facility (higher risk scores are in red shades).
    - Hurricane paths are displayed as colored lines, with special events marked along the paths.
    - You can filter the facilities and hurricanes displayed using the sidebar filters.
""")
