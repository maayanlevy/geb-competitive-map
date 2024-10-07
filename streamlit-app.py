import streamlit as st
import pandas as pd
import urllib.parse
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import streamlit.components as components
import base64

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
        background-color: #f0f0f0;
        border: 1px solid #ccc;
    }
    .company-logo {
        position: absolute;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background-size: cover;
        background-position: center;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .company-logo:hover {
        transform: scale(1.1);
    }
    .axis-label {
        position: absolute;
        font-weight: bold;
    }
    .group-label {
        position: absolute;
        font-weight: bold;
        font-size: 14px;
        color: #555;
    }
    </style>
    <div class="competitive-map">
    """

    # Add axis labels
    map_html += """
    <div class="axis-label" style="top: 10px; left: 50%;">Customized</div>
    <div class="axis-label" style="bottom: 10px; left: 50%;">Zero-shot</div>
    <div class="axis-label" style="top: 50%; left: 10px; transform: rotate(-90deg);">Models</div>
    <div class="axis-label" style="top: 50%; right: 10px; transform: rotate(90deg);">DIY</div>
    """

    # Add group labels
    groups = [
        ("Zero Reasoning", 50, 90),
        ("DIY Reasoning", 90, 50),
        ("Customized reasoning", 50, 10),
        ("Reasoning Models", 10, 50)
    ]
    for group, x, y in groups:
        map_html += f'<div class="group-label" style="left: {x}%; top: {y}%;">{group}</div>'

    # Add company logos
    for _, company in df.iterrows():
        x = company.get('x', 50)  # Default to center if not specified
        y = company.get('y', 50)  # Default to center if not specified
        logo_url = company['Logo']
        company_name = company['Company']
        map_html += f"""
        <div class="company-logo" style="left: {x}%; top: {y}%; background-image: url('{logo_url}');"
             onclick="selectCompany('{company_name}');" title="{company_name}"></div>
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

    # Create and display the competitive map
    st.subheader("Competitive Map")
    map_html = create_competitive_map(df)
    st.components.v1.html(map_html, height=650, scrolling=False)

    # Add JavaScript to handle messages from the iframe
    st.markdown(
        """
        <script>
        window.addEventListener('message', function(event) {
            if (event.data.type === 'company_selected') {
                const company = event.data.company;
                console.log('Received company in parent:', company);
                document.dispatchEvent(new CustomEvent('company_selected', {detail: company}));
            }
        });
        </script>
        """,
        unsafe_allow_html=True
    )

    # Use a custom component to receive the selected company
    selected_company = st.components.v1.declare_component("company_selector", path=None)
    new_selection = selected_company()

    if new_selection and new_selection != st.session_state.selected_company:
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
        st.write("Click on a company logo to see its details.")

if __name__ == "__main__":
    main()