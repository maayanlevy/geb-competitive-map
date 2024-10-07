import streamlit as st
import pandas as pd
import urllib.parse
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import streamlit.components as components
import base64
import math
import random

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
        width: 40px;
        height: 40px;
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
        border-radius: 50%;
        cursor: pointer;
        transition: transform 0.2s;
        margin-bottom: 10px;
    }
    .company-logo:hover {
        transform: scale(1.1);
    }
    .company-name {
        position: absolute;
        top: 100%;
        left: 50%;
        transform: translateX(-50%);
        background-color: rgba(255, 255, 255, 0.7);
        padding: 2px 4px;
        border-radius: 3px;
        font-size: 8px;
        max-width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .axis-label {
        position: absolute;
        font-weight: bold;
        color: #FFA500;
        font-size: 14px;
    }
    .sub-label {
        position: absolute;
        font-size: 12px;
        color: #FFA500;
    }
    .bucket-label {
        position: absolute;
        font-size: 14px;
        color: #008080;
        font-weight: bold;
        top: 5px;
        left: 5px;
    }
    .bucket-area {
        position: absolute;
        border: 1px solid #008080;
        border-radius: 15px;
        padding: 10px 10px 5px 10px;
    }
    .axis-line {
        position: absolute;
        background-color: #A9A9A9;
    }
    .arrow-head {
        width: 0;
        height: 0;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        position: absolute;
    }
    </style>
    <div class="competitive-map">
    """

    # Add axis lines with arrow heads
    map_html += """
    <div class="axis-line" style="left: 50%; top: 5%; width: 1px; height: 90%;"></div>
    <div class="arrow-head" style="left: 50%; top: 5%; transform: translateX(-50%); border-bottom: 10px solid #A9A9A9;"></div>
    <div class="arrow-head" style="left: 50%; bottom: 5%; transform: translateX(-50%) rotate(180deg); border-bottom: 10px solid #A9A9A9;"></div>
    <div class="axis-line" style="left: 5%; top: 50%; width: 90%; height: 1px;"></div>
    <div class="arrow-head" style="left: 5%; top: 50%; transform: translateY(-50%) rotate(-90deg); border-bottom: 10px solid #A9A9A9;"></div>
    <div class="arrow-head" style="right: 5%; top: 50%; transform: translateY(-50%) rotate(90deg); border-bottom: 10px solid #A9A9A9;"></div>
    """

    # Add axis labels
    map_html += """
    <div class="axis-label" style="top: 10px; left: 50%; transform: translateX(-50%);">Custom Reasoning</div>
    <div class="axis-label" style="bottom: 10px; left: 50%; transform: translateX(-50%);">Model Reasoning</div>
    <div class="axis-label" style="top: 50%; left: 10px; transform: rotate(-90deg) translateY(-50%);">Generic Processes</div>
    <div class="axis-label" style="top: 50%; right: 10px; transform: rotate(90deg) translateY(-50%);">My Processes</div>
    """

    # Add sub-labels with margin from axis
    sub_labels = [
        ("Multi Tenancy", 50.5, 10),
        ("Multi System", 50.5, 20),
        ("System Flows", 50.5, 37),
        ("Action Models", 50.5, 63),
        ("Generic Task", 50.5, 83),
        ("Generic Prompts", 17, 51),
        ("My Data", 32, 51),
        ("Customized Prompts", 47, 51),
        ("My Tools", 62, 51),
        ("Custom Flows", 77, 51),
        ("Organization", 92, 51)
    ]
    for label, x, y in sub_labels:
        map_html += f'<div class="sub-label" style="left: {x}%; top: {y}%;">{label}</div>'

    # Calculate bucket sizes based on company count
    bucket_counts = df['bucket'].value_counts()

    bucket_positions = {
        "Customized AI": (25, 25),
        "Enterprise Search": (15, 60),
        "Out of the Box Agents": (10, 85),
        "Vertical AI": (30, 70),
        "UI Models": (60, 6),
        "Reasoning Models": (60, 85),
        "DIY AI": (60, 25)
    }

    for bucket, (bucket_x, bucket_y) in bucket_positions.items():
        company_count = bucket_counts.get(bucket, 0)
        
        # Calculate bucket size based on company count
        cols = 4
        rows = max(3, math.ceil(company_count / cols))  # Default to 3 rows minimum
        width = cols * 45 + 20  # 45px per logo, 20px padding
        height = rows * 55 + 30  # 55px per row (including margin), 30px padding for label

        map_html += f"""
        <div class="bucket-area" style="left: {bucket_x}%; top: {bucket_y}%; width: {width}px; height: {height}px;">
            <div class="bucket-label">{bucket} ({company_count})</div>
        """
        
        bucket_companies = df[df['bucket'] == bucket]
        for i in range(rows * cols):
            row = i // cols
            col = i % cols
            x = 10 + (col * 45)
            y = 25 + (row * 55)  # Increased vertical spacing
            
            if i < len(bucket_companies):
                company = bucket_companies.iloc[i]
                company_name = company['Company']
                logo_url = company['Logo']
                map_html += f"""
                <div class="company-logo" style="left: {x}px; top: {y}px; background-image: url('{logo_url}');"
                     onclick="selectCompany('{company_name}');" title="{company_name}">
                    <span class="company-name">{company_name}</span>
                </div>
                """
            else:
                # Add empty placeholder for uniform grid
                map_html += f"""
                <div class="company-logo" style="left: {x}px; top: {y}px; background-image: none;"></div>
                """
        
        map_html += "</div>"

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

# Main Streamlit app
def main():
    st.title("Competitive Map")

    # Initialize session state
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'selected_company' not in st.session_state:
        st.session_state.selected_company = None

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

    # Create and display the competitive map
    st.subheader("Competitive Map")
    map_html = create_competitive_map(non_ignored_companies)
    st.components.v1.html(map_html, height=650, scrolling=False)

    # Add JavaScript to handle messages from the iframe
    st.markdown(
        """
        <script>
        window.addEventListener('message', function(event) {
            if (event.data.type === 'company_selected') {
                const company = event.data.company;
                console.log('Received company in parent:', company);
                const selectElement = document.querySelector('select[data-testid="stSelectbox"]');
                if (selectElement) {
                    selectElement.value = company;
                    selectElement.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }
        });
        </script>
        """,
        unsafe_allow_html=True
    )

    # Use a Streamlit callback to handle company selection
    def handle_company_selection():
        selected_company = st.session_state.get('selected_company_input')
        if selected_company and selected_company != st.session_state.selected_company:
            st.session_state.selected_company = selected_company
            st.rerun()

    # Dropdown to select company
    company_list = non_ignored_companies['Company'].tolist()
    st.selectbox("Select a company", options=company_list, key="selected_company_input", on_change=handle_company_selection, index=None)

    # Company details section
    st.subheader("Company Details")
    if st.session_state.selected_company:
        company_name = st.session_state.selected_company
        company_row = df[df['Company'] == company_name]
        
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