import pandas as pd  # pip install pandas openpyxl
# import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
import time
import random
import requests
import json
#import sessionState
from xlsx2json import convert_xlsx
from csv2json import convert_csv, convert_csv_action_name
from services_api import get_token, export_data, tql_data, import_data, import_text, single_report_export

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="API BETA PLAYGROUND",
                   page_icon=":pie_chart:", layout="wide")

st.sidebar.subheader("Configuration :")
url_input = st.sidebar.text_input(
    "Please add the portal URL (include the ending /): ", '')
user_pwd = st.sidebar.file_uploader(
    "Please upload your binary format user and password file")

# if user_pwd is not None:
#    if url_input is not None:
#        token = get_token(
# S            f"{url_input}rest/v1/auth", user_pwd)
# username = st.sidebar.text_input("Enter username")
# password = st.sidebar.text_input("Enter a password", type="password")

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

# st.sidebar.subheader("Please Choose Endpoint:")
# endpoint_selected = st.sidebar.selectbox("Endpoints: ", endpoint_options)
# endpoint = endpoint_selected
st.sidebar.subheader("Select Data Service:")

services_selected = st.sidebar.radio(
    "Please select one from followings", ["intro", "data exports", "TQL", "TQL Table Join Service", "xlsx/csv to json conversion", "json-imports", "csv-imports", "TQL-Report-Pivot Service"])
# 'account.region=2&serviceModel=DISPATCH_SERVICE_MODEL'

if services_selected == "intro":
    st.subheader("Instruction")
    st.markdown(
        "The data services tool is built on-top of the TrackTik api which can handle data-related work, such as DATA EXPORT from api endpoints, TQL export, join data from 2 different TQL exports, data file conversion and data imports either json or csv."
        "Please NOTE this tool is NOT running on TrackTik platform and it’s running on non-commercial server, it’s NOT for external usage and should NOT be shared with clients.")
    st.subheader("Authentication")
    st.markdown(
        "Please add the portal URL in the configuration section and upload the json file which contains the user and password")
    st.subheader("Data Export")
    st.markdown(
        "API GET request at single data endpoint. All available data endpoints are listed. The relational data attributs are not exposed")
    st.subheader("TQL")
    st.markdown(
        "TQL section provides both pre-built TQL queries and query input section where you can build TQL and fetch data")
    st.subheader("TQL Table Join Service")
    st.markdown(
        "As TQL doesn't provide join function, this section will help join 2 different TQL query data into 1 table")
    st.subheader("xlsx2json And csv2json Conversion")
    st.markdown(
        "To convert a xlsx or a csv file into batch/file format, make sure following requirements are met")
    st.markdown(
        "* For xlsx make sure all sheet/tab has a name, the name should be the endpoint. e.g. clients, positions, regions")
    st.markdown(
        "* For csv, make sure input the endpoint in the left side bar under endpoint section")
    st.subheader("json Import")
    st.markdown(
        "With batch/file json data, you can use this service to send API request to upload the data, which can be data creation and data update. Please make sure all the data follows TrackTik API specification for each data endpoint")
    st.subheader("csv Import")
    st.markdown(
        "This service will upload the csv data file into your portal via TrackTik API. The logic is data tool will convert the csv file into batch/file json data and then upload data to portal via API. Please make sure the csv file is built according to data requirements and all attributes (columns and values) follow TrackTik API specification for each data endpoint")
if services_selected == "data exports":
    if user_pwd is not None:
        st.subheader(f"Data Export Services")
        st.subheader("Please Choose Endpoint:")
        endpoint_selected = st.selectbox("Endpoints: ", endpoint_options)
        endpoint = endpoint_selected
        submit = st.button('Export Data')
        if submit:
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
        if url_input is not None:
            token = get_token(
                f"{url_input}rest/v1/auth", user_pwd)

        st.subheader(f"TQL Query Services")
        query_endpoint = st.selectbox(
            "Available Query Example: ", tql_endpoint_options)
        sample_query = tql_options.loc[tql_options['tql_resource']
                                       == query_endpoint, 'TQL'].iloc[0]
        tql_query = st.text_area(
            label="Please Build Your Own Query Here: ", value=sample_query, height=None)

        if len(tql_query) > 0:
            df = tql_data(token, url_input, tql_query)
            st.text(f"The QUERY data: ")
            st.dataframe(df)

            st.download_button(
                label="Download data as CSV",
                data=df.to_csv(sep=',', encoding='utf-8', index=False),
                file_name=f'QUER-data-export.csv',
                mime='text/csv',
            )

if services_selected == "TQL Table Join Service":
    if user_pwd is not None:
        if url_input is not None:
            token = get_token(
                f"{url_input}rest/v1/auth", user_pwd)

            col1, col2 = st.columns(2)
            with col1:
                st.subheader(f"TQL table1")
                query_endpoint1 = st.selectbox(
                    "Available Query Examples: ", tql_endpoint_options, key="0001221a")
                sample_query1 = tql_options.loc[tql_options['tql_resource']
                                                == query_endpoint1, 'TQL'].iloc[0]
                tql_query1 = st.text_area(
                    label="Please Build Your Own Query Here: ", height=None, value=sample_query1, key="0001223a")

                if len(tql_query1) > 0:
                    df1 = tql_data(token, url_input, tql_query1)
                    option1 = st.text(f"The QUERY data 1: ")
                    st.dataframe(df1, 2000, 200)
                    st.download_button(
                        label="Download data as CSV",
                        data=df1.to_csv(
                            sep=',', encoding='utf-8', index=False),
                        file_name=f'Joined-data-export.csv',
                        mime='text/csv', key="0001223buttona"
                    )

            with col2:
                st.subheader(f"TQL table2")
                query_endpoint2 = st.selectbox(
                    "Available Query Examples: ", tql_endpoint_options, key="0001221b")
                sample_query2 = tql_options.loc[tql_options['tql_resource']
                                                == query_endpoint2, 'TQL'].iloc[0]
                tql_query2 = st.text_area(
                    label="Please Build Your Own Query Here: ", height=None, value=sample_query2, key="0001223b")

                if len(tql_query2) > 0:
                    df2 = tql_data(token, url_input, tql_query2)
                    option2 = st.text(f"The QUERY data 2: ")
                    st.dataframe(df2, 2000, 200)
                    st.download_button(
                        label="Download data as CSV",
                        data=df2.to_csv(
                            sep=',', encoding='utf-8', index=False),
                        file_name=f'Joined-data-export.csv',
                        mime='text/csv', key="0001223buttonb"
                    )

            st.subheader(f"JOIN Table1 AND Table2")
            if df1 is not None:
                if df2 is not None:
                    key1, key2, key3, key4, key5 = st.columns(5)
                    with key1:
                        table1_key = st.selectbox(
                            "key1", df1.columns, key="0001224a")
                    with key2:
                        table3_join = st.selectbox(
                            "join method", ["left", "right", "outer", "inner", "cross"], key="0001224c")
                    with key3:
                        table2_key = st.selectbox(
                            "key2", df2.columns, key="0001224b")
                    submit = st.button('Join The Tables')
                    if submit:
                        joined_data = pd.merge(
                            df1, df2, left_on=table1_key, right_on=table2_key, how=table3_join)
                        st.text(f"The joined data is: ")
                        st.dataframe(joined_data, 2000, 200)
                        st.download_button(
                            label="Download data as CSV",
                            data=joined_data.to_csv(
                                sep=',', encoding='utf-8', index=False),
                            file_name=f'Joined-data-export.csv',
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
        "Please define the **ENDPOINT** in the box and include * in front field names for lookups")
    box1, box2, box3 = st.columns(3)
    with box1:
        endpoint_selected = st.selectbox("Endpoints: ", endpoint_options)
        endpoint = endpoint_selected
    with box2:
        action_type = st.selectbox(
            "action type: ", ["REPLACE", "CREATE", "UPDATE", "EXECUTE"])
    with box3:
        action_name = st.text_input("action name: ", '')

    uploaded_csv = st.file_uploader(
        "Please upload the csv file to convert into BATCH import json file")
    if uploaded_csv is not None:
        # To read file as bytes:
        if action_type != 'EXECUTE':
            bytes_data = convert_csv(uploaded_csv, endpoint, action_type)
            st.text(f"The {uploaded_csv.name} converted JSON file is: ")
            st.write(bytes_data)
            st.download_button(
                label="Download json",
                data=json.dumps(bytes_data),
                file_name=f'{uploaded_csv.name.replace(".csv","")}-batch-file.json'
            )
        if action_type == 'EXECUTE':
            bytes_data = convert_csv_action_name(
                uploaded_csv, endpoint, action_name)
            st.text(f"The {uploaded_csv.name} converted JSON file is: ")
            st.write(bytes_data)
            st.download_button(
                label="Download json",
                data=json.dumps(bytes_data),
                file_name=f'{uploaded_csv.name.replace(".csv","")}-batch-file.json')

if services_selected == "json-imports":
    st.subheader(f"Data Import Services - TrackTik Internal Use Only")
    file_to_import = st.file_uploader(
        "please upload your json batch file")
    if file_to_import is not None:
        submit = st.button('Import Selected File')
        if submit:
            data = import_data(url_input, user_pwd, file_to_import)
            st.text(f"The {file_to_import.name} import result is: ")
            st.write(data)
if services_selected == "csv-imports":
    st.subheader("convert **_csv2json_** batch file and import service")
    st.markdown(
        "Please define the **ENDPOINT** in the box and include * in front field names for lookups")
    box1, box2, box3 = st.columns(3)
    with box1:
        endpoint_selected = st.selectbox("Endpoints: ", endpoint_options)
        endpoint = endpoint_selected
    with box2:
        action_type = st.selectbox(
            "action type: ", ["REPLACE", "CREATE", "UPDATE", "EXECUTE"])
    with box3:
        action_name = st.text_input("action name: ", '')

    uploaded_csv = st.file_uploader(
        "Please upload the csv file to convert into BATCH import json file")
    if uploaded_csv is not None:
        # To read file as bytes:
        if action_type != 'EXECUTE':
            bytes_data = convert_csv(uploaded_csv, endpoint, action_type)
            st.text(f"The {uploaded_csv.name} converted JSON file is: ")
            st.write(bytes_data)
            json_data = json.dumps(bytes_data)

            if json_data is not None:
                submit = st.button('Import Selected File')
                if submit:
                    data = import_text(url_input, user_pwd, json_data)
                    st.text(f"The {endpoint} import result is: ")
                    st.write(data)

        if action_type == 'EXECUTE':
            bytes_data = convert_csv_action_name(
                uploaded_csv, endpoint, action_name)
            st.text(f"The {uploaded_csv.name} converted JSON file is: ")
            st.write(bytes_data)
            json_data = json.dumps(bytes_data)

            if bytes_data is not None:
                submit = st.button('Import Selected File')
                if submit:
                    data = import_text(url_input, user_pwd, json_data)
                    st.text(f"The {endpoint} import result is: ")
                    st.write(data)

if services_selected == "TQL-Report-Pivot Service":
    if user_pwd is not None:
        if url_input is not None:
            token = get_token(f"{url_input}rest/v1/auth", user_pwd)
            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
            with col1:
                reportTemplate = st.text_input(
                    "report template is: ", '', key="0001224232a")
            with col2:
                accounts = st.text_input(
                    "account id list is: ", '', key="0001224232b")
            with col3:
                startDate = st.text_input(
                    "start date: ", '', key="0001224232c")
            with col4:
                endDate = st.text_input("end date: ", '', key="0001224232d")
            submit = st.button('Export Report')
            if submit:
                if reportTemplate is not None:
                    report_data = single_report_export(
                        token, url_input, reportTemplate, accounts, startDate, endDate)
                    st.text(f"The report export data: ")
                    st.dataframe(report_data, 2000, 200)
                    st.download_button(
                        label=f"Download report {reportTemplate} data as CSV",
                        data=report_data.to_csv(
                            sep=',', encoding='utf-8', index=True),
                        file_name=f"report_{reportTemplate}_export.csv",
                        mime='text/csv',
                    )

            # with open("tql_report_batch_export_beta1.csv", newline='', encoding='utf-8') as file:
            #     btn = st.download_button(
            #         label="download demo report metric file_https://innovation.staffr.net/",
            #         data=file,
            #         file_name="tql_report_batch_export_beta.csv",
            #         mime="text/csv"
            #     )
            # report_metric_file = st.file_uploader(
            #     "Please upload the report metric file")
            # # file_direct = st.text_input(
            # #    "Please add file directory (make sure us '/'): ", '')
            # if report_metric_file is not None:
            #     batch_report_export(
            #         token, url_input, report_metric_file)

    # ---SIDEBAR---
