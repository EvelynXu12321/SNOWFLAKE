import streamlit as st

st.title("Information & Resources")

# what is social vulnerability
st.subheader("Why Social Vulnerability Matters")
st.markdown(
    """
    Natural disasters impact communities differently. Social vulnerability measures how factors like **income, 
    age, healthcare access, and housing quality** affect a community’s ability to prepare for and recover 
    from hurricanes. Identifying these risks helps improve disaster response and support at-risk populations.
    """
)

with st.expander("⁉️ Did you know"):
    st.markdown(
        """
        **Case Study: Hurricane Katrina (2005)**
        - Communities with **high social vulnerability** faced greater challenges in evacuation and recovery.
        - Many lacked access to **transportation, emergency resources, or financial means** to rebuild.
        - The aftermath showed the importance of **early preparation and targeted assistance** for vulnerable populations.
        """
    )

# How the prediction model works
st.subheader("🔬 How Our Prediction Model Works")

st.markdown(
    """
    Our model uses machine learning to assess social vulnerability based on multiple datasets, including:
    - **📍 FEMA National Risk Index (NRI)** – Assess risk scores and expected annual losses from hurricanes and other natural hazards
    - **📊 Social Vulnerability Index (SVI)** – Population demographics, income, and disabilities
    - **🌀 HURDAT2 Hurricane Data** – Historical hurricane paths & intensities
    - **🏥 Diversity, Equity, and Inclusion - Social Determinants of Health** – Insights into social determinants like income, education, and healthcare access
    - **🏚️ Critical Facilities in Florida (Overpass Turbo)** – Location data for critical facilities like hospitals, clinics, and shelters
    """
)

st.subheader("📌 How to Use the Predictions")

st.markdown(
    """
    - **Search Your Location**: Enter your county or ZIP code to view risk scores.
    - **Understand the Risk Levels**: High-risk areas need more preparedness.
    - **Compare Past Hurricanes**: View historical damage and responses.
    """
)

with st.expander("⚠️ Understanding Risk Scores"):
    st.markdown(
        """
        - **Low (0-3)**: Minimal risk, good infrastructure.
        - **Moderate (4-6)**: Some vulnerabilities, medium resilience.
        - **High (7-10)**: High-risk zone, needs strong preparedness.
        """
    )

# Preparedness and resources
st.subheader("🛑 Hurricane Preparedness Resources")

# Emergency preparedness tips -- link to FEMA, CDC, Red Cross resources
st.markdown(
    """
    **Stay informed and take action before a disaster strikes:**
    - **[FEMA Disaster Preparedness](https://www.ready.gov/hurricanes)**
    - **[Red Cross Hurricane Safety](https://www.redcross.org/get-help/how-to-prepare-for-emergencies/types-of-emergencies/hurricane.html)**
    - **[National Hurricane Center](https://www.nhc.noaa.gov/)**
    """
)

st.video("https://www.youtube.com/watch?v=ZKdgmNUCjEY&t=4s")  # hurricane safety video

# Evacuation planning -- links to evacuation routes and shelters
st.markdown(
    """
    **Evacuation planning is crucial for safety:**

    Many states have designated evacuation zones and predetermined routes.
    - **[FEMA Evacuation Guide: Planning Considerations](https://www.fema.gov/sites/default/files/2020-07/planning-considerations-evacuation-and-shelter-in-place.pdf)**
    - **[Flash Find Your Evacuation Zone](https://hurricanestrong.org/wp-content/uploads/2021/04/5-5-21-Find-Your-Evacuation-Zone-Landing-Page-Final.pdf)**
    - **[Ready Make a Plan](https://www.ready.gov/evacuating-yourself-and-your-family)**
    """
)

# Emergency kit -- what to include in an emergency kit
st.markdown(
    """
    **How to Build a Disaster Supply Kit:**
    - **[FEMA Disaster Supply Kit](https://www.ready.gov/build-a-kit)**
    - **[Flash Disaster Supply Kit](https://flash.org/how-to-build-a-disaster-supply-kit/)**
    """
)

st.video("https://www.youtube.com/watch?v=CqbBB3s14_8")  # disaster supply kit video

# Community support programs -- links to local resources
st.markdown(
    """
    **Community support programs can help during disasters:**
    - **[FEMA Disaster Assistance](https://www.fema.gov/assistance/individual)**
    - **[American Red Cross Find Nearby Shelters](https://www.redcross.org/get-help/how-to-prepare-for-emergencies/types-of-emergencies/hurricane.html)**
    """
)

st.subheader("📌 Project Repository")

st.markdown(
    """
    View the full codebase on [GitHub](https://github.com/EvelynXu12321/SNOWFLAKE).
    """
)

# Disclaimer
st.subheader("Disclaimer")
st.markdown(
    """
    The information provided on this site is for educational purposes only and should not be considered as 
    professional advice. Always consult with local authorities and emergency services for guidance during 
    disasters.
    """
)