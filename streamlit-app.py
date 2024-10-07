import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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
        result = sheet.values().get(spreadsheetId='1CSkJwokWSGwJDRkUMLokv0CI9ENXUWi9qjbvzGoIjSA', 
                                    range='Sheet1').execute()
        data = result.get('values', [])
        df = pd.DataFrame(data[1:], columns=data[0])
        return df
    except HttpError as err:
        st.error(f"An error occurred: {err}")
        return pd.DataFrame()

# Function to create company card
def create_company_card(company_data):
    return f"""
    <div class="company-card" onclick="showDetails('{company_data['Company']}')">
        <img src="{company_data['Logo']}" alt="{company_data['Company']} logo" style="width:50px; height:50px; object-fit:contain;">
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
        }
        .row {
            display: flex;
            flex: 1;
        }
        .quadrant {
            flex: 1;
            border: 1px solid #ddd;
            padding: 10px;
            overflow-y: auto;
        }
        .company-card {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
            cursor: pointer;
        }
        .company-card img {
            margin-right: 10px;
        }
    </style>
    <div class="map-container">
    """
    
    for i in range(0, 4, 2):
        map_html += '<div class="row">'
        for j in range(2):
            bucket = buckets[i+j]
            bucket_data = df[df['bucket'] == bucket]
            map_html += f'<div class="quadrant"><h3>{bucket}</h3>'
            for _, company in bucket_data.iterrows():
                map_html += create_company_card(company)
            map_html += '</div>'
        map_html += '</div>'
    
    map_html += """
    </div>
    <script>
    function showDetails(company) {
        window.parent.postMessage({type: 'company_selected', company: company}, '*');
    }
    </script>
    """
    return map_html

# Main Streamlit app
def main():
    st.title("Competitive Map")

    # Fetch data
    df = fetch_data()

    if df.empty:
        st.warning("No data available. Please check your Google Sheets connection.")
        return

    # Create and display the competitive map
    map_html = create_competitive_map(df)
    st.components.v1.html(map_html, height=650)

    # Company details section
    st.subheader("Company Details")
    selected_company = st.empty()

    # JavaScript to handle company selection
    st.components.v1.html("""
    <script>
    window.addEventListener('message', function(event) {
        if (event.data.type === 'company_selected') {
            window.parent.postMessage({type: 'update_streamlit', company: event.data.company}, '*');
        }
    }, false);
    </script>
    """)

    # Handle company selection
    if selected_company:
        company_data = df[df['Company'] == selected_company].iloc[0]
        st.write(f"**Description:** {company_data['description']}")
        st.write(f"**Location:** {company_data['Location']}")
        st.write(f"**Employees:** {company_data['Employees']}")
        st.write(f"**Stage:** {company_data['Stage']}")
        st.write(f"**Website:** {company_data['Website']}")
        st.write(f"**Investors:** {company_data['Investors']}")
        st.write(f"**Comments:** {company_data['Comments']}")
        st.image(company_data['Logo'], width=100)

if __name__ == "__main__":
    main()