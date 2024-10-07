import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

# Configure Streamlit page
st.set_page_config(layout="wide", page_title="Competitive Map")

# Set up Google Sheets API credentials
creds = service_account.Credentials.from_service_account_info(
    {
        "type": st.secrets["type"],
        "project_id": st.secrets["project_id"],
        "private_key_id": st.secrets["private_key_id"],
        "private_key": st.secrets["private_key"],
        "client_email": st.secrets["client_email"],
        "client_id": st.secrets["client_id"],
        "auth_uri": st.secrets["auth_uri"],
        "token_uri": st.secrets["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["client_x509_cert_url"]
    },
    scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
)

# Function to fetch data from Google Sheets
def fetch_data():
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId='1CSkJwokWSGwJDRkUMLokv0CI9ENXUWi9qjbvzGoIjSA', range='Sheet1').execute()
    data = result.get('values', [])
    df = pd.DataFrame(data[1:], columns=data[0])
    return df

# Function to create the competitive map
def create_competitive_map(df):
    fig = go.Figure()

    buckets = ['Zero Reasoning', 'DIY Reasoning', 'Customized reasoning', 'Reasoning Models']
    colors = ['rgb(141, 211, 199)', 'rgb(255, 255, 179)', 'rgb(190, 186, 218)', 'rgb(251, 128, 114)']

    for i, bucket in enumerate(buckets):
        bucket_data = df[df['bucket'] == bucket]
        x = [0.25 + (i % 2) * 0.5] * len(bucket_data)
        y = [0.25 + (i // 2) * 0.5] * len(bucket_data)
        
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='markers+text',
            marker=dict(size=50, color=colors[i], opacity=0.6),
            text=bucket_data['Company'],
            textposition="top center",
            hoverinfo='text',
            name=bucket
        ))

    fig.update_layout(
        showlegend=False,
        height=600,
        xaxis=dict(range=[0, 1], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[0, 1], showgrid=False, zeroline=False, visible=False),
        annotations=[
            dict(x=0.25, y=1, xref="paper", yref="paper", text="Generic", showarrow=False),
            dict(x=0.75, y=1, xref="paper", yref="paper", text="My processes", showarrow=False),
            dict(x=0, y=0.75, xref="paper", yref="paper", text="Model reasoning", showarrow=False, textangle=-90),
            dict(x=0, y=0.25, xref="paper", yref="paper", text="My reasoning", showarrow=False, textangle=-90)
        ]
    )

    return fig

# Function to create company card
def create_company_card(company_data):
    st.subheader(company_data['Company'])
    st.write(f"**Description:** {company_data['description']}")
    st.write(f"**Location:** {company_data['Location']}")
    st.write(f"**Employees:** {company_data['Employees']}")
    st.write(f"**Stage:** {company_data['Stage']}")
    st.write(f"**Website:** {company_data['Website']}")
    st.write(f"**Investors:** {company_data['Investors']}")
    st.write(f"**Comments:** {company_data['Comments']}")
    st.image(company_data['Logo'], width=100)

# Main Streamlit app
def main():
    st.title("Competitive Map")

    # Fetch data
    df = fetch_data()

    # Create competitive map
    fig = create_competitive_map(df)

    # Display the map
    st.plotly_chart(fig, use_container_width=True)

    # Company details section
    st.subheader("Company Details")
    selected_company = st.selectbox("Select a company", df['Company'].tolist())
    
    if selected_company:
        company_data = df[df['Company'] == selected_company].iloc[0]
        create_company_card(company_data)

if __name__ == "__main__":
    main()