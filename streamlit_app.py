import altair as alt
import pandas as pd
import streamlit as st

# Page configuration
st.set_page_config(
    layout="wide"  # Wide layout
)

# Load CSS file
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# File paths to datasets
file_paths = [
    'data/01_District_wise_crimes_committed_IPC_2013.csv',
    'data/02_01_District_wise_crimes_committed_against_SC_2001_2012.csv',
    'data/01_District_wise_crimes_committed_IPC_2014.csv',
    # Add more files as needed
]

# Read and combine the datasets
dataframes = [pd.read_csv(file_path) for file_path in file_paths]
data = pd.concat(dataframes, ignore_index=True)

# Crime categories to visualize
crime_columns = ['Murder', 'Rape', 'Kidnapping and Abduction', 'Arson', 'Grievous Hurt']

# Sidebar for navigation
st.sidebar.title("Navigation")
option = st.sidebar.selectbox(
    "Select a view:",
    ("Home", "Crime Data Visualization")
)

# Home Page
if option == "Home":
    st.markdown(
        """
        <div class="homepage-container">
            <h1 class="title" style= "color:red" >Welcome to the Crime Navigator App</h1>
            <p class="description" style= "color:red">
                Explore, analyze, and gain insights into crime data across states and cities in India.
            </p>
            <div class="features">
                <h3>Features of this App</h3>
                <ul>
                    <li><strong>Crime Data Visualization</strong> View detailed crime statistics for selected regions.</li>
                    <li><strong>Compare Crime Rates</strong> Compare crime data across districts within a state.</li>
                </ul>
            </div>
            <div class="upcoming-features">
                <h3>Upcoming Features</h3>
                <ul>
                    <li><strong>Danger Levels</strong> Assess the safety of cities based on reported crimes.</li>
                    <li><strong>Women Safety Insights</strong> Analyze crimes affecting women with focused data visualizations.</li>
                </ul>
            </div>
            <p class="footer">
              ⬅️⬅️  Use the <strong>sidebar</strong> to navigate and explore the app’s features.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )




# Crime Data Visualization Page
elif option == "Crime Data Visualization":
    
    # Dropdown for state selection
    states = data['States/UTs'].unique()
    selected_state = st.selectbox('Select a state:', states)

    # Filter the data for the selected state
    state_data = data[data['States/UTs'] == selected_state]

    # Dropdown for city selection (within the selected state)
    cities_in_state = state_data['District'].unique()
    selected_city = st.selectbox('Select a city in the state:', cities_in_state)

    # Filter data based on the selected city
    city_data = state_data[state_data['District'] == selected_city]
   
    # Ensure States/UTs and District are at the start
    columns_order = ['States/UTs', 'District'] + [col for col in city_data.columns if col not in ['States/UTs', 'District']]
    reordered_city_data = city_data[columns_order]

    # Remove columns with all None/NaN values
    filtered_city_data = reordered_city_data.dropna(axis=1, how='all')

    # Display filtered data
    st.subheader(f'Crime Data for {selected_city} in {selected_state}')
    st.write(filtered_city_data)


    # Data Visualization: Show crime counts per category
    st.subheader(f'Crime Statistics in {selected_city}')
    # Dynamically handle columns available in the dataset
    available_columns = [col for col in crime_columns if col in city_data.columns]

    # Sum of crimes for each available category
    crime_counts = city_data[available_columns].sum()
    # Sort the crime counts in descending order
    sorted_crime_counts = crime_counts.sort_values(ascending=True)

    # Display the sorted crime counts
    st.bar_chart(sorted_crime_counts)

    # Comparison Visualization: Crime data for all cities in the selected state
    st.subheader(f'Crime Comparison in {selected_state}')
    state_crime_totals = state_data.groupby('District')[available_columns].sum().reset_index()

    # Add a 'Total' row to the dataset
    total_row = state_crime_totals[available_columns].sum()
    total_row['District'] = 'Total'
    state_crime_totals = pd.concat([state_crime_totals, pd.DataFrame([total_row])], ignore_index=True)

    # Filter out the 'Total' row from the chart
    chart_data = state_crime_totals[state_crime_totals['District'] != 'Total']

    state_crime_chart = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X('District:N', title='District'),
        y=alt.Y('sum(Murder):Q', title='Total Murders'),
        color=alt.Color('District:N', legend=None),
        tooltip=[alt.Tooltip(col, title=col) for col in available_columns]
    ).properties(
        title=f'Comparison of Crime across Cities in {selected_state}'
    )
    st.altair_chart(state_crime_chart, use_container_width=True)


