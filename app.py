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
from services_api import export_data, tql_data, import_data, import_text, single_report_export
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
import csv
import re
import asyncio,sys
import subprocess


# Fix Windows limitation with asyncio subprocess
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="API BETA PLAYGROUND",
                   page_icon=":pie_chart:", layout="wide")

st.sidebar.subheader("Configuration :")


url_input = st.sidebar.text_input(
    "Please add the portal URL (include the ending /): ", '')
#user_pwd = st.sidebar.file_uploader(
#    "Please upload your binary format user and password file")
token = st.sidebar.text_input(
    "Paste the api token here", '')
#if user_pwd is not None:
#    token = get_token(f"{url_input}rest/v1/auth", user_pwd)


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
    "Please select one from followings", ["intro", "data exports", "TQL", "TQL Table Join Service", "split-csv", "xlsx/csv to json conversion", "json-imports", "csv-imports", "PDF report DOWNLOAD", "TQL-Single-Report-Pivot Service", "TQL-Multi-Reports-Pivot Service"])
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
    if token is not None:
        # token = get_token(
        #    f"{url_input}rest/v1/auth", user_pwd)
        st.subheader(f"Data Export Services")
        st.subheader("Please Choose Endpoint:")
        endpoint_selected = st.selectbox("Endpoints: ", endpoint_options)
        endpoint = endpoint_selected
        submit = st.button('Export Data')
        if submit:
            df = export_data(endpoint, token, url_input)
            st.text(f"The {endpoint} data: ")
            st.dataframe(df)

            st.download_button(
                label="Download data as CSV",
                data=df.to_csv(sep=',', encoding='utf-8', index=False),
                file_name=f'{endpoint}-data-export.csv',
                mime='text/csv',
            )

if services_selected == "TQL":

    if token is not None:

        # if url_input is not None:
        #    token = get_token(
        #        f"{url_input}rest/v1/auth", user_pwd)

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
    if token is not None:
        if url_input is not None:

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

if services_selected == "split-csv":
    source_file = st.file_uploader("file to split")
    split1, split2 = st.columns(2)
    with split1:
        splitsize = st.text_input("split size: ", '')
    if source_file is not None:
        if splitsize is not None:

            for i, chunk in enumerate(pd.read_csv(source_file, chunksize=int(splitsize),encoding='utf-8')):
                st.download_button(
                    label="Download data as CSV",
                    data=chunk.to_csv(
                        sep=',', encoding='utf-8', index=False),
                    file_name=f'{source_file.name.replace(".CSV","")}_{i}.csv',
                    mime='application/csv',
                )
                st.dataframe(chunk, 2000, 200)

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
    box1, box2, box3, box4 = st.columns(4)
    with box1:
        endpoint_selected = st.selectbox("endpoints: ", endpoint_options)
        endpoint = endpoint_selected
    with box2:
        action_type = st.selectbox(
            "action type: ", ["REPLACE", "CREATE", "UPDATE", "EXECUTE"])
    with box3:
        action_name = st.text_input("action name: ", '')
    with box4:
        list_field = st.text_input("array field: ", '')

    uploaded_csv = st.file_uploader(
        "Please upload the csv file to convert into BATCH import json file")
    if uploaded_csv is not None:
        # To read file as bytes:
        if action_type != 'EXECUTE':
            bytes_data = convert_csv(uploaded_csv, endpoint, action_type)
            if list_field == '':
                
                st.text(f"The {uploaded_csv.name} converted JSON file is: ")
                st.write(bytes_data)
                st.download_button(
                    label="Download json",
                    data=json.dumps(bytes_data),
                    file_name=f'{uploaded_csv.name.replace(".csv","")}-batch-file.json'
                )
            if list_field != '':
                for item in bytes_data['operations']:
                    a=list(item['data'][f'{list_field}'].values())
                    if '{' in a[0]:
                        list_dict = []
                        for i in a:
                            list_dict.append(json.loads(i))
                        item['data'][f'{list_field}'] = list_dict
                        
                    else:
                        item['data'][f'{list_field}'] = a
                
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
            if list_field == '':
                
                st.text(f"The {uploaded_csv.name} converted JSON file is: ")
                st.write(bytes_data)
                st.download_button(
                    label="Download json",
                    data=json.dumps(bytes_data),
                    file_name=f'{uploaded_csv.name.replace(".csv","")}-batch-file.json'
                )
            if list_field != '':
                for item in bytes_data['operations']:
                    a=list(item['data'][f'{list_field}'].values())
                    if '{' in a[0]:
                        list_dict = []
                        for i in a:
                            list_dict.append(json.loads(i))
                        item['data'][f'{list_field}'] = list_dict
                        
                    else:
                        item['data'][f'{list_field}'] = a
                
                st.text(f"The {uploaded_csv.name} converted JSON file is: ")
                st.write(bytes_data)
                st.download_button(
                    label="Download json",
                    data=json.dumps(bytes_data),
                    file_name=f'{uploaded_csv.name.replace(".csv","")}-batch-file.json'
                )



if services_selected == "json-imports":
    st.subheader(f"Data Import Services - TrackTik Internal Use Only")
    file_to_import = st.file_uploader(
        "please upload your json batch file")
    if file_to_import is not None:
        submit = st.button('Import Selected File')
        if submit:
            data = import_data(url_input, token, file_to_import)
            st.text(f"The {file_to_import.name} import result is: ")
            st.write(data)
if services_selected == "csv-imports":
    st.subheader("convert **_csv2json_** batch file and import service")
    st.markdown(
        "Please define the **ENDPOINT** in the box and include * in front field names for lookups")
    box1, box2, box3, box4 = st.columns(4)
    with box1:
        endpoint_selected = st.selectbox("endpoints: ", endpoint_options)
        endpoint = endpoint_selected
    with box2:
        action_type = st.selectbox(
            "action type: ", ["REPLACE", "CREATE", "UPDATE", "EXECUTE"])
    with box3:
        action_name = st.text_input("action name: ", '')

    with box4:
        list_field = st.text_input("array field: ", '')

    uploaded_csv = st.file_uploader(
        "Please upload the csv file to convert into BATCH import json file")
    if uploaded_csv is not None:
        # To read file as bytes:
        if action_type != 'EXECUTE':
            bytes_data = convert_csv(uploaded_csv, endpoint, action_type)
            
            if list_field == '':
                #st.text(f"The {uploaded_csv.name} converted JSON file is: ")
                #st.write(bytes_data)
                st.text(f"The {uploaded_csv.name} converted JSON file is: ")
                st.write(bytes_data)
                json_data = json.dumps(bytes_data)

            if list_field != '':
                for item in bytes_data['operations']:
                    a=list(item['data'][f'{list_field}'].values())
                    
                    if '{' in a[0]:
                        list_dict = []
                        for i in a:
                            list_dict.append(json.loads(i))
                        item['data'][f'{list_field}'] = list_dict
                        
                    else:
                        item['data'][f'{list_field}'] = a
                    
                st.text(f"The {uploaded_csv.name} converted JSON file is: ")
                st.write(bytes_data)
                json_data = json.dumps(bytes_data)

            if json_data is not None:
                submit = st.button('Import Selected File')
                if submit:
                    data = import_text(url_input, token, json_data)
                    st.text(f"The {endpoint} import result is: ")
                    st.write(data)

        if action_type == 'EXECUTE':
            bytes_data = convert_csv_action_name(
                uploaded_csv, endpoint, action_name)
            if list_field == '':
                #st.text(f"The {uploaded_csv.name} converted JSON file is: ")
                #st.write(bytes_data)
                st.text(f"The {uploaded_csv.name} converted JSON file is: ")
                st.write(bytes_data)
                json_data = json.dumps(bytes_data)

            if list_field != '':
                for item in bytes_data['operations']:
                    a=list(item['data'][f'{list_field}'].values())
                    if '{' in a[0]:
                        list_dict = []
                        for i in a:
                            list_dict.append(json.loads(i))
                        item['data'][f'{list_field}'] = list_dict
                        
                    else:
                        item['data'][f'{list_field}'] = a
                st.text(f"The {uploaded_csv.name} converted JSON file is: ")
                st.write(bytes_data)
                json_data = json.dumps(bytes_data)

            if bytes_data is not None:
                submit = st.button('Import Selected File')
                if submit:
                    data = import_text(url_input, token, json_data)
                    st.text(f"The {endpoint} import result is: ")
                    st.write(data)


if services_selected == "PDF report DOWNLOAD":
    st.subheader("PDF Report Download Service - TrackTik Internal Use Only")
    st.markdown(
        "This service downloads bulk PDF reports using a CSV with columns: **id, reportname, account.name, date**"
    )
    uploaded_csv = st.file_uploader("Upload the CSV file")

    username = st.text_input("Enter username")
    password = st.text_input("Enter password", type="password")
    login_url = url_input
    report_base_url = url_input + "patrol/default/viewreportprintable/idreport/"

    # ---------- LOGIN BUTTON ----------
    if st.button("Login"):
        result = subprocess.run(
            ["python", "playwright_login.py", username, password, login_url],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            st.success("✅ Logged in and cookies saved!")
        else:
            st.error(f"❌ Login failed:\n{result.stderr}")

    # ---------- FILE UPLOAD ----------
    if uploaded_csv is not None:
        report_list = pd.read_csv(uploaded_csv, dtype=str)
        report_id = report_list["id"]
        reportname = report_list["reportname"]
        account = report_list["account.name"]
        date = report_list["date"]

        # Helper to make filenames safe
        def safe_filename(s):
            return re.sub(r'[\\/*?:"<>|]', "_", str(s))

        # Load cookies
        try:
            with open("cookies.json", "r") as f:
                cookies = json.load(f)
        except FileNotFoundError:
            st.error("❌ Cookies not found. Please login first.")
            st.stop()

        cookie_dict = {cookie["name"]: cookie["value"] for cookie in cookies}
        session = requests.Session()
        for name, value in cookie_dict.items():
            session.cookies.set(name, value)

        headers = {"User-Agent": "Mozilla/5.0"}

        # Loop through reports
        for i in range(len(report_id)):
            filename = (
                f"{safe_filename(reportname[i])}_"
                f"{safe_filename(account[i])}_"
                f"{safe_filename(date[i])}_({report_id[i]}).pdf"
            )
            pdf_url = f"{report_base_url}{report_id[i]}"
            r = session.get(pdf_url, headers=headers)

            if r.status_code == 200 and r.content.startswith(b"%PDF"):
                with open(filename, "wb") as f:
                    f.write(r.content)
                st.success(f"✅ Saved {filename}")
            else:
                st.error(f"❌ Failed {report_id[i]}, status: {r.status_code}")
              
if services_selected == "TQL-Single-Report-Pivot Service":

    if token is not None:
        if url_input is not None:
           
            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
            with col1:
                reportTemplate = st.text_input(
                    "*report template id list is: ", key="0001224232a")
            with col2:
                accounts = st.text_input(
                    "account id list is: ", '', key="0001224232b")
            with col3:
                startDate = st.text_input(
                    "*start date: ", '', key="0001224232c")
            with col4:
                endDate = st.text_input("*end date: ", '', key="0001224232d")
            submit = st.button('Export Report')
            if submit:
                if reportTemplate is not None:
                    report_data = single_report_export(
                        token, url_input, reportTemplate, accounts, startDate, endDate)
                    st.text(f"The report export data: ")
                    st.dataframe(report_data, 2000, 500)
                    st.download_button(
                        label=f"Download report {reportTemplate} data as CSV",
                        data=report_data.to_csv(
                            sep=',', encoding='utf-8', index=True),
                        file_name=f"report_{reportTemplate}_export.csv",
                        mime='text/csv',
                    )

if services_selected == "TQL-Multi-Reports-Pivot Service":
    st.subheader("report value export service")
    st.markdown(
        "make sure all the required fields filled up, for report template list and account list please separate by ',' and leave NO space")
    if token is not None:
        if url_input is not None:
            # token = get_token(f"{url_input}rest/v1/auth", user_pwd)
            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
            with col1:
                reportTemplate = st.text_input(
                    "report template is: ", key="0001224232a")
            with col2:
                accounts = st.text_input(
                    "account id list is: ", '', key="0001224232b")
            with col3:
                startDate = st.text_input(
                    "start date: ", '', key="0001224232c")
            with col4:
                endDate = st.text_input("end date: ", '', key="0001224232d")

            if len(startDate) > 0 and len(endDate) > 0:
                if len(reportTemplate) > 0:
                    template_list = reportTemplate.split(",")
                    for i, template in enumerate(template_list):
                        report_data = single_report_export(
                            token, url_input, template, accounts, startDate, endDate)
                        st.download_button(
                            label=f"Download report {template} data as CSV",
                            data=report_data.to_csv(
                                sep=',', encoding='utf-8', index=True),
                            file_name=f"report_{template}_export.csv",
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


