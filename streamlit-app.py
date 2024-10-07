import streamlit as st
import pandas as pd
import urllib.parse
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import streamlit.components as components
import base64
import math

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


def create_competitive_map(df):
    map_html = """
    <style>
    .competitive-map {
        position: relative;
        width: 100%;
        height: 600px;
        background-color: #ffffff;
        font-family: Arial, sans-serif;
    }
    .company-logo {
        position: absolute;
        width: 80px;
        height: 80px;
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        cursor: pointer;
        transition: transform 0.2s;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        align-items: center;
    }
    .company-logo:hover {
        transform: scale(1.1);
    }
    .company-name {
        background-color: rgba(255, 255, 255, 0.7);
        padding: 2px 4px;
        border-radius: 3px;
        font-size: 10px;
        max-width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .axis-label {
        position: absolute;
        font-weight: bold;
        color: #FFA500;
    }
    .sub-label {
        position: absolute;
        font-size: 12px;
        color: #FFA500;
    }
    .main-label {
        position: absolute;
        font-size: 16px;
        color: #A9A9A9;
    }
    .bucket-label {
        position: absolute;
        font-size: 14px;
        color: #008080;
        font-weight: bold;
    }
    </style>
    <div class="competitive-map">
    """

    # Add axis labels
    map_html += """
    <div class="axis-label" style="top: 10px; left: 50%; transform: translateX(-50%);">Custom Reasoning</div>
    <div class="axis-label" style="bottom: 10px; left: 50%; transform: translateX(-50%);">Model Reasoning</div>
    <div class="axis-label" style="top: 50%; left: 10px; transform: rotate(-90deg) translateY(-50%);">Generic Processes</div>
    <div class="axis-label" style="top: 50%; right: 10px; transform: rotate(90deg) translateY(-50%);">My Processes</div>
    """

    # Add sub-labels
    sub_labels = [
        ("Multi Tenancy", 50, 15),
        ("Multi System", 50, 25),
        ("System Flows", 50, 35),
        ("Action Models", 50, 65),
        ("Generic Task", 50, 85),
        ("Generic Prompts", 15, 50),
        ("My Data", 30, 50),
        ("Customized Prompts", 45, 50),
        ("My Tools", 60, 50),
        ("Custom Flows", 75, 50),
        ("Organization", 90, 50)
    ]
    for label, x, y in sub_labels:
        map_html += f'<div class="sub-label" style="left: {x}%; top: {y}%;">{label}</div>'

    # Add main labels
    main_labels = [
        ("Generic Processes", 5, 95),
        ("My Processes", 85, 95)
    ]
    for label, x, y in main_labels:
        map_html += f'<div class="main-label" style="left: {x}%; top: {y}%;">{label}</div>'

    # Add bucket labels and company logos
    bucket_positions = {
        "Customized AI": (70, 30),
        "Enterprise Search": (30, 70),
        "Out of the Box Agents": (50, 50),
        "Vertical AI": (30, 30),
        "UI Models": (70, 70),
        "Reasoning Models": (50, 80),
        "DIY AI": (80, 50)
    }

    for bucket, (bucket_x, bucket_y) in bucket_positions.items():
        map_html += f'<div class="bucket-label" style="left: {bucket_x}%; top: {bucket_y}%;">{bucket}</div>'
        
        bucket_companies = df[df['bucket'] == bucket]
        company_count = len(bucket_companies)
        for i, (_, company) in enumerate(bucket_companies.iterrows()):
            angle = 2 * 3.14159 * i / company_count
            radius = 10  # Adjust this value to change the spread of companies around the bucket label
            x = bucket_x + radius * math.cos(angle)
            y = bucket_y + radius * math.sin(angle)
            company_name = company['Company']
            logo_url = company['Logo']
            map_html += f"""
            <div class="company-logo" style="left: {x}%; top: {y}%; background-image: url('{logo_url}');"
                 onclick="selectCompany('{company_name}');" title="{company_name}">
                <span class="company-name">{company_name}</span>
            </div>
            """

    map_html += """
    </div>
    <script>
    function selectCompany(companyName) {
        console.log("Company selected:", companyName);
        window.parent.postMessage({type: 'company_selected', company: companyName}, '*');
    }
    </script>
    """
    return map_html

def select_company(company_name):
    st.session_state.selected_company = company_name

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

    # Filter out companies with "ignore" in their bucket
    if 'bucket' in df.columns:
        non_ignored_companies = df[df['bucket'].str.lower() != 'ignore']
    else:
        non_ignored_companies = df
    
    # Select the first non-ignored company by default
    if st.session_state.selected_company is None and not non_ignored_companies.empty:
        st.session_state.selected_company = non_ignored_companies.iloc[0]['Company']

    # Create and display the competitive map
    st.subheader("Competitive Map")
    map_html = create_competitive_map(non_ignored_companies)  # Only pass non-ignored companies
    st.components.v1.html(map_html, height=650, scrolling=False)

    # Add JavaScript to handle messages from the iframe
    st.markdown(
        """
        <script>
        window.addEventListener('message', function(event) {
            if (event.data.type === 'company_selected') {
                const company = event.data.company;
                console.log('Received company in parent:', company);
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
        st.rerun()

    # Company details section
    st.subheader("Company Details")
    if st.session_state.selected_company:
        company_name = st.session_state.selected_company
        company_row = df[df['Company'].str.strip().str.lower() == company_name.strip().lower()]
        
        if not company_row.empty:
            company_data = company_row.iloc[0]
            
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
        st.write("No company selected.")

if __name__ == "__main__":
    main()