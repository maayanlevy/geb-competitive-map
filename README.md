# Competitive Map Streamlit App

This Streamlit application creates a competitive map (VC style) with 4 buckets, each containing a list of company icons. The app fetches data from a Google Spreadsheet and displays it in an interactive 2x2 grid layout.

## Features

- Interactive 2x2 grid layout representing different categories
- Company logos and names grouped by category
- Clickable company icons that display detailed information
- Data fetched dynamically from a Google Spreadsheet
- Responsive design for various screen sizes

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/competitive-map-streamlit.git
   cd competitive-map-streamlit
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up Google Sheets API:
   - Create a Google Cloud project and enable the Google Sheets API
   - Create a service account and download the JSON key file
   - Set up environment variables with the service account credentials (see Configuration section)

## Configuration

To run this app, you need to set up the following environment variables with your Google Sheets API credentials:

- `GOOGLE_TYPE`
- `GOOGLE_PROJECT_ID`
- `GOOGLE_PRIVATE_KEY_ID`
- `GOOGLE_PRIVATE_KEY`
- `GOOGLE_CLIENT_EMAIL`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_AUTH_URI`
- `GOOGLE_TOKEN_URI`
- `GOOGLE_AUTH_PROVIDER_X509_CERT_URL`
- `GOOGLE_CLIENT_X509_CERT_URL`

For local development, you can create a `.env` file in the root directory with these variables. For deployment, set these variables in your hosting platform's environment settings.

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and go to `http://localhost:8501` (or the URL provided by Streamlit).

3. The app will display the competitive map with company icons grouped into four categories.

4. Click on a company icon to view detailed information about that company.

## Data Source

The app fetches data from a Google Spreadsheet with the ID `1CSkJwokWSGwJDRkUMLokv0CI9ENXUWi9qjbvzGoIjSA`. Ensure that your Google service account has read access to this spreadsheet.

## Deployment

This app can be deployed on any platform that supports Streamlit applications, such as Streamlit Cloud, Heroku, or Google Cloud Run. Make sure to set the environment variables with your Google Sheets API credentials in your deployment environment.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.