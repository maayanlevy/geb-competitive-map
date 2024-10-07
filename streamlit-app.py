import streamlit as st
import pandas as pd
import urllib.parse
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import streamlit.components as components

# Configure Streamlit page
st.set_page_config(layout="wide", page_title="Competitive Map")

# Set up Google Sheets API credentials
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
)

# Function to fetch data from Google Sheets
def fetch_data():
    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId='1CSkJwokWSGwJDRkUMLokv0CI9ENXUWi9qjbvzGoIjSA',  # Replace with your actual Spreadsheet ID
            range='Sheet1'
        ).execute()
        data = result.get('values', [])
        if not data:
            st.warning("No data found in the spreadsheet.")
            return pd.DataFrame()
        columns = [col.strip() for col in data[0]]  # Strip whitespace from column names
        df = pd.DataFrame(data[1:], columns=columns)
        return df
    except HttpError as err:
        st.error(f"An error occurred: {err}")
        return pd.DataFrame()

# Function to create company card
def create_company_card(company_data):
    company_name = company_data['Company'].replace("'", "\\'")
    return f"""
    <div class="company-card" onclick="selectCompany('{company_name}')">
        <img src="{company_data['Logo']}" alt="{company_data['Company']} logo">
        <p>{company_data['Company']}</p>
    </div>
    """

# Function to create the competitive map
def create_competitive_map(df):
    buckets = ['Zero Reasoning', 'DIY Reasoning', 'Customized reasoning', 'Reasoning Models']
    map_html = """
    <style>
        .map-container {
            display: flex;
            flex-direction: column;
            height: 600px;
            border: 1px solid #ddd;
            position: relative;
        }
        .row {
            display: flex;
            flex: 1;
        }
        .quadrant {
            flex: 1;
            border: 1px solid #ddd;
            padding: 10px;
            display: flex;
            flex-direction: column;
        }
        .companies-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: flex-start;
            overflow-y: auto;
        }
        .company-card {
            width: 100px;
            text-align: center;
            margin: 5px;
            cursor: pointer;
        }
        .company-card img {
            width: 50px;
            height: 50px;
            object-fit: cover;
            border-radius: 50%;
        }
        .company-card p {
            margin: 5px 0;
            font-size: 12px;
        }
        /* Axis styles */
        .axis {
            position: absolute;
            background-color: #000;
        }
        .x-axis {
            width: 100%;
            height: 2px;
            top: 50%;
            left: 0;
        }
        .y-axis {
            width: 2px;
            height: 100%;
            top: 0;
            left: 50%;
        }
        .arrow {
            position: absolute;
            width: 0;
            height: 0;
            border-style: solid;
        }
        .x-arrow {
            border-width: 5px 0 5px 10px;
            border-color: transparent transparent transparent #000;
            top: 50%;
            right: 0;
            transform: translateY(-50%);
        }
        .y-arrow {
            border-width: 10px 5px 0 5px;
            border-color: #000 transparent transparent transparent;
            left: 50%;
            top: 0;
            transform: translateX(-50%);
        }
        .axis-label {
            position: absolute;
            font-size: 12px;
            color: #000;
        }
        .x-label-left {
            top: 50%;
            left: 5px;
            transform: translateY(-50%);
        }
        .x-label-right {
            top: 50%;
            right: 5px;
            transform: translateY(-50%);
        }
        .y-label-top {
            left: 50%;
            top: 5px;
            transform: translateX(-50%);
        }
        .y-label-bottom {
            left: 50%;
            bottom: 5px;
            transform: translateX(-50%);
        }
    </style>
    <div class="map-container">
    """
    for bucket in buckets:
        bucket_data = df[df['bucket'].str.strip().str.lower() == bucket.lower()]
        map_html += f'''
            <div class="row">
                <div class="quadrant">
                    <h3>{bucket}</h3>
                    <div class="companies-container">
                '''
        for _, company in bucket_data.iterrows():
            map_html += create_company_card(company)
        map_html += '</div></div>'
    map_html += '</div>'
    # Add axes and labels
    map_html += """
        <div class="axis x-axis"></div>
        <div class="axis y-axis"></div>
        <div class="arrow x-arrow"></div>
        <div class="arrow y-arrow"></div>
        <div class="axis-label x-label-left">Generic</div>
        <div class="axis-label x-label-right">My processes</div>
        <div class="axis-label y-label-top">Model reasoning</div>
        <div class="axis-label y-label-bottom">My reasoning</div>
    </div>
    <script>
    function selectCompany(companyName) {
        console.log("selectCompany called with:", companyName);
        window.parent.postMessage({type: "company_selected", company: companyName}, "*");
    }
    </script>
    """
    return map_html

import streamlit.components.v1 as components

# Main Streamlit app
def main():
    st.title("Competitive Map")

    # Initialize session state
    if 'selected_company' not in st.session_state:
        st.session_state.selected_company = None
    if 'df' not in st.session_state:
        st.session_state.df = None

    # Add a refresh button
    if st.button("Refresh Data"):
        st.session_state.df = None  # Clear the cached data

    # Fetch data only if it hasn't been fetched before or refresh button was clicked
    if st.session_state.df is None:
        with st.spinner("Fetching data..."):
            st.session_state.df = fetch_data()

    df = st.session_state.df

    if df.empty:
        st.warning("No data available. Please check your Google Sheets connection.")
        return

    # Create and display the competitive map
    map_html = create_competitive_map(df)
    st.components.v1.html(map_html, height=650, scrolling=True)

    # Add JavaScript to handle messages
    st.markdown(
        """
        <script>
        window.addEventListener('message', function(event) {
            if (event.data.type === 'company_selected') {
                const company = event.data.company;
                console.log('Received company:', company);
                document.getElementById('selected-company-input').value = company;
                document.getElementById('update-button').click();
            }
        });
        </script>
        """,
        unsafe_allow_html=True
    )

    # Hidden input and button to update selected company
    selected_company = st.empty()
    new_selection = selected_company.text_input("Selected Company", key="selected-company-input", label_visibility="hidden")
    
    # Hide the update button using CSS
    st.markdown("""
        <style>
        #update-button {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)
    
    update_button = st.button("Update", key="update-button")

    if update_button and new_selection != st.session_state.selected_company:
        st.session_state.selected_company = new_selection

    # Company details section
    st.subheader("Company Details")
    st.write("Debug - Current selected_company:", st.session_state.selected_company)

    if st.session_state.selected_company:
        company_name = st.session_state.selected_company
        if 'Company' in df.columns:
            company_row = df[df['Company'].str.strip().str.lower() == company_name.strip().lower()]
            
            if not company_row.empty:
                company_data = company_row.iloc[0]
                
                # Display company details
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image(company_data['Logo'], width=100)
                with col2:
                    st.markdown(f"**Company:** {company_name}")
                    st.markdown(f"**Description:** {company_data.get('description', 'N/A')}")
                    st.markdown(f"**Location:** {company_data.get('Location', 'N/A')}")
                    st.markdown(f"**Employees:** {company_data.get('Employees', 'N/A')}")
                    st.markdown(f"**Stage:** {company_data.get('Stage', 'N/A')}")
                    st.markdown(f"**Website:** [{company_data.get('Website', '')}]({company_data.get('Website', '')})")
                    st.markdown(f"**Investors:** {company_data.get('Investors', 'N/A')}")
                    st.markdown(f"**Comments:** {company_data.get('Comments', 'N/A')}")
            else:
                st.warning("Company details not found.")
        else:
            st.error("The 'Company' column is missing in the data.")
    else:
        st.write("Click on a company logo to see its details.")

if __name__ == "__main__":
    main()