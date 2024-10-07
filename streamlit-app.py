import streamlit as st
import pandas as pd
import urllib.parse
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
        result = sheet.values().get(
            spreadsheetId='1CSkJwokWSGwJDRkUMLokv0CI9ENXUWi9qjbvzGoIjSA',
            range='Sheet1'
        ).execute()
        data = result.get('values', [])
        df = pd.DataFrame(data[1:], columns=data[0])
        return df
    except HttpError as err:
        st.error(f"An error occurred: {err}")
        return pd.DataFrame()

# Function to create company card
def create_company_card(company_data):
    return f"""
    <div class="company-card" onclick="selectCompany('{company_data['Company']}')">
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
            justify-content: space-around;
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
            width: 0;
            height: 0;
            border-style: solid;
            position: absolute;
        }
        .x-arrow {
            border-width: 5px 0 5px 10px;
            border-color: transparent transparent transparent #000;
            top: 50%;
            right: 0;
            transform: translateY(-50%);
        }
        .y-arrow {
            border-width: 0 5px 10px 5px;
            border-color: transparent transparent #000 transparent;
            left: 50%;
            top: 0;
            transform: translateX(-50%);
        }
        .axis-label {
            position: absolute;
            font-size: 12px;
        }
        .x-label-left {
            left: 10px;
            top: 50%;
            transform: translateY(-50%);
        }
        .x-label-right {
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
        }
        .y-label-top {
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
        }
        .y-label-bottom {
            bottom: 10px;
            left: 50%;
            transform: translateX(-50%);
        }
    </style>
    <div class="map-container">
    """

    for i in range(0, 4, 2):
        map_html += '<div class="row">'
        for j in range(2):
            if i + j < len(buckets):
                bucket = buckets[i + j]
                bucket_data = df[df['bucket'] == bucket]
                map_html += f'''
                <div class="quadrant">
                    <h3>{bucket}</h3>
                    <div class="companies-container">
                '''
                for _, company in bucket_data.iterrows():
                    map_html += create_company_card(company)
                map_html += '</div></div>'
        map_html += '</div>'

    map_html += """
        <div class="axis x-axis"></div>
        <div class="axis y-axis"></div>
        <div class="arrow x-arrow"></div>
        <div class="arrow y-arrow"></div>
        <div class="axis-label x-label-left">Generic</div>
        <div class="axis-label x-label-right">My processes</div>
        <div class="axis-label y-label-top">Model reasoning</div>
        <div class="axis-label y-label-bottom">My reasoning</div>
    <script>
    function selectCompany(companyName) {
        window.parent.postMessage({type: 'company_selected', company: companyName}, '*');
    }
    </script>
    </div>
    """
    return map_html

# Main Streamlit app
def main():
    st.title("Competitive Map")

    # Initialize session state
    if 'selected_company' not in st.session_state:
        st.session_state.selected_company = None

    # Fetch data
    df = fetch_data()

    if df.empty:
        st.warning("No data available. Please check your Google Sheets connection.")
        return

    # Create and display the competitive map
    map_html = create_competitive_map(df)
    st.components.v1.html(map_html, height=650)

    # JavaScript to handle company selection
    st.components.v1.html("""
    <script>
    window.addEventListener('message', function(event) {
        if (event.data.type === 'company_selected') {
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: event.data.company}, '*');
        }
    }, false);
    </script>
    """)

    # Update session state when a company is selected
    selected_company = st.experimental_get_query_params().get('selected_company', [None])[0]
    if selected_company:
        st.session_state.selected_company = selected_company

    # Company details section
    st.subheader("Company Details")
    
    if st.session_state.selected_company:
        company_name = st.session_state.selected_company
        company_row = df[df['Company'] == company_name]
        if not company_row.empty:
            company_data = company_row.iloc[0]
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(company_data['Logo'], width=100)
            with col2:
                st.write(f"**Company:** {company_name}")
                st.write(f"**Description:** {company_data['description']}")
                st.write(f"**Location:** {company_data['Location']}")
                st.write(f"**Employees:** {company_data['Employees']}")
                st.write(f"**Stage:** {company_data['Stage']}")
                st.write(f"**Website:** [{company_data['Website']}]({company_data['Website']})")
                st.write(f"**Investors:** {company_data['Investors']}")
                st.write(f"**Comments:** {company_data['Comments']}")
        else:
            st.warning("Company details not found.")
    else:
        st.write("Click on a company logo to see its details.")

    # Clear the query parameters after displaying the details
    st.experimental_set_query_params()

if __name__ == "__main__":
    main()