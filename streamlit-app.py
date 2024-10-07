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

    # Debug: Display DataFrame columns and first few rows
    st.write("**DataFrame Columns:**", df.columns.tolist())
    st.write("**DataFrame Sample:**")
    st.dataframe(df.head())

    # Create and display the competitive map
    map_html = create_competitive_map(df)
    selected_company = st.components.v1.html(map_html, height=650, scrolling=True)

    # Debug: Display selected company from HTML component
    if selected_company is not None:
        st.write("**Selected Company from HTML Component:**", str(selected_company))

    # Update session state if a company was selected
    if selected_company is not None:
        st.session_state.selected_company = str(selected_company)

    # Company details section
    st.subheader("Company Details")

    if st.session_state.selected_company:
        company_name = st.session_state.selected_company
        if 'Company' in df.columns:
            # Ensure company_name is a string
            if isinstance(company_name, str):
                company_row = df[df['Company'].str.strip().str.lower() == company_name.strip().lower()]
            else:
                st.error("Selected company name is not a valid string.")
                return
        else:
            st.error("The 'Company' column is missing in the data.")
            return

        # Debug: Display selected company name and matching rows
        st.write(f"**Selected Company Name:** {company_name}")
        st.write("**Matching Rows:**")
        st.dataframe(company_row)

        if not company_row.empty:
            company_data = company_row.iloc[0]

            # Display logo and company details
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