import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
import requests
import json
from xlsx2json import convert_xlsx
from csv2json import convert_csv
from services_api import get_token, export_data, tql_data, import_data

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="API BETA PLAYGROUND",
                   page_icon=":pie_chart:", layout="wide")

st.sidebar.subheader("Configuration :")
url_input = st.sidebar.text_input(
    "Please add the portal URL (include the ending /): ", '')
user_pwd = st.sidebar.file_uploader(
    "Please upload your binary format user and password file")
#username = st.sidebar.text_input("Enter username")
#password = st.sidebar.text_input("Enter a password", type="password")

# user_pwd = json.dumps(
#     {
#         "username": f"{username}",
#         "password": f"{password}"
#     }
# )
endpoint_options = list(pd.read_csv(
    'api_objects.csv', dtype=str)['endpoint'])
tql_options = pd.read_csv(
    'data-tql-collections.csv', dtype=str)
tql_endpoint_options = tql_options['tql_resource']

st.sidebar.subheader("Please Choose Endpoint:")
endpoint_selected = st.sidebar.selectbox("Endpoints: ", endpoint_options)
endpoint = endpoint_selected
st.sidebar.subheader("Select Data Service:")

services_selected = st.sidebar.radio(
    "Please select one from followings", ["intro", "data exports", "TQL", "xlsx/csv to json conversion", "data imports"])
# 'account.region=2&serviceModel=DISPATCH_SERVICE_MODEL'

if services_selected == "intro":
    st.subheader("Data Export")
    st.markdown(
        "To export a collection of data objects, please provide URL and json formatted user and password file")
    st.subheader("xlsx2json And csv2json Conversion")
    st.markdown(
        "To convert a xlsx or a csv file into batch/file format, make sure following requirements are met")
    st.markdown(
        "* For xlsx make sure all sheet/tab has a name, the name should be the endpoint. e.g. clients, positions, regions")
    st.markdown(
        "* For csv, make sure input the endpoint in the left side bar under endpoint section")
    st.subheader("Data Import")
    st.markdown(
        "To use data import services, please add the portal URL address and username/password file. Then broswe and upload the batch json file")
if services_selected == "data exports":
    if user_pwd is not None:
        st.subheader(f"Data Export Services")
        df = export_data(endpoint, user_pwd, url_input)
        st.text(f"The {endpoint} data: ")
        st.dataframe(df)

        st.download_button(
            label="Download data as CSV",
            data=df.to_csv(sep=',', encoding='utf-8', index=False),
            file_name=f'{endpoint}-data-export.csv',
            mime='text/csv',
        )

if services_selected == "TQL":
    if user_pwd is not None:
        st.subheader(f"TQL Query Services")
        query_endpoint = st.selectbox(
            "Available Queries: ", tql_endpoint_options)
        sample_query = tql_options.loc[tql_options['tql_resource']
                                       == query_endpoint, 'TQL'].iloc[0]
        tql_query = st.text_area(
            label="Please Type Query Here: ", value=sample_query, height=None)

        if len(tql_query) > 0:
            df = tql_data(user_pwd, url_input, tql_query)
            st.text(f"The QUERY data: ")
            st.dataframe(df)

            st.download_button(
                label="Download data as CSV",
                data=df.to_csv(sep=',', encoding='utf-8', index=False),
                file_name=f'QUER-data-export.csv',
                mime='text/csv',
            )

if services_selected == "xlsx/csv to json conversion":
    st.subheader("Batch Import File Convert Services - **_xlsx2json_**")
    st.markdown(
        "Please define the **ENDPOINT** in sheet name and include * in front field names for lookups")
    uploaded_xlsx = st.file_uploader(
        "Please upload the xlsx file to convert into BATCH import json file")
    if uploaded_xlsx is not None:
        # To read file as bytes:
        bytes_data = convert_xlsx(uploaded_xlsx)
        st.text(f"The {uploaded_xlsx.name} converted JSON file is: ")
        st.write(bytes_data)
        st.download_button(
            label="Download json",
            data=json.dumps(bytes_data),
            file_name=f'{uploaded_xlsx.name.replace(".xlsx","")}-batch-file.json'
        )

    st.subheader("Batch Import File Convert Services - **_csv2json_**")
    st.markdown(
        "Please define the **ENDPOINT** in the left side bar and include * in front field names for lookups")
    uploaded_csv = st.file_uploader(
        "Please upload the csv file to convert into BATCH import json file")
    if uploaded_csv is not None:
        # To read file as bytes:
        bytes_data = convert_csv(uploaded_csv, endpoint)
        st.text(f"The {uploaded_csv.name} converted JSON file is: ")
        st.write(bytes_data)
        st.download_button(
            label="Download json",
            data=json.dumps(bytes_data),
            file_name=f'{uploaded_csv.name.replace(".csv","")}-batch-file.json'
        )

if services_selected == "data imports":
    st.subheader(f"Data Import Services - TrackTik Internal Use Only")
    file_to_import = st.file_uploader(
        "please upload your json batch file")
    if file_to_import is not None:
        submit = st.button('Import Selected File')
        if submit:
            data = import_data(url_input, user_pwd, file_to_import)
            st.text(f"The {file_to_import.name} import result is: ")
            st.write(data)

# ---SIDEBAR---
