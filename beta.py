import pandas as pd  # pip install pandas openpyxl
# import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
import requests
import json
# from xls2json import build_import

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="API BETA PLAYGROUND",
                   page_icon=":bar_chart:", layout="wide")

st.sidebar.header("Please Put Endpoint Here:")
endpoint_selected = st.sidebar.text_input("Endpoints: ", 'regions')


def get_token(url, access):

    #with open(access) as json_file:
    #    payload = json.load(json_file)
    payload = access

    headers = {
        'Content-Type': 'application/json',
        'Cookie': 'PHPSESSID=1gtjjjlkt2cm1jr4mgp2rsodqeegifg8'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    token = response.json()['auth']['token']

    return token


endpoint = endpoint_selected
# 'account.region=2&serviceModel=DISPATCH_SERVICE_MODEL'
params = None
api_objects = pd.read_csv(
    'api_objects.csv', dtype=str)

#params = api_objects.loc[api_objects['endpoint'] == endpoint, 'params'].item()
lookup = api_objects.loc[api_objects['endpoint']
                         == endpoint, 'lookup'].item()
fields = api_objects.loc[api_objects['endpoint']
                         == endpoint, 'fields'].item()
lookup_list = lookup.split(",")
param_path = "resource="+endpoint+"&lookups=" + lookup+"&fields="+fields+"&" + \
    params if params != None else "resource=" + \
    endpoint+"&lookups=" + lookup+"&fields="+fields
#path = 'G:/My Drive/ds_working_python - BETA/source_file'
user_pwd = st.file_uploader(
    "Please put your pwd")

if user_pwd is not None:
  token = get_token(
    "https://dataservicetracktik.guards.app/rest/v1/auth", user_pwd)
  payload = {}
  headers = {
      'Authorization': 'Bearer '+token,
      'Cookie': 'PHPSESSID=vqru8j08ho4oe1uaht3d6mikchqak2or'
  }
  response = requests.request(
      "GET", "https://dataservicetracktik.guards.app/rest/v1/batch/file?" + param_path, headers=headers, data=payload)
  data = response.json()
  df = pd.json_normalize(data=data['operations']).filter(regex='^data.')
  df.columns = df.columns.str.replace("data.", "", regex=True)
  st.dataframe(df)
  
  st.download_button(
      label="Download data as CSV",
      data=df.to_csv(sep=',', encoding='utf-8', index=False),
      file_name=f'{endpoint}-data-export.csv',
      mime='text/csv',
  )

uploaded_file = st.file_uploader(
    "Please choose a XSL file to convert into BATCH import json file")
def build_dict(data_source, row):
    column = list(data_source.columns)
    dict_temp = {}
    for i in column:
        if '.' in i:
            key_parent = i[0:i.find('.')]
            key_child = i[i.find('.')+1:len(i)]
            if key_parent in dict_temp.keys():
                dict_temp[f'{key_parent}'].update(
                    {f'{key_child}': f"{data_source[f'{i}'][row]}"})
            else:
                dict_temp.update(
                    {f'{key_parent}': {f'{key_child}': f"{data_source[f'{i}'][row]}"}})
        else:
            dict_temp.update({f"{i}": f"{data_source[f'{i}'][row]}"})

    return dict_temp


def build_lookup(lookuplist, data_source, row):
    lookup_temp = {}
    for i in lookuplist:
        lookup_temp.update({f"{i}": f"{data_source[f'{i}'][row]}"})
    return lookup_temp


def build_import(template_file):
    # from .import build_dict
    source_to_import = {"onFailure": "ABORT", "operations": []}
    endpoint_list = pd.ExcelFile(template_file).sheet_names
    api_objects = pd.read_csv(
        'api_objects.csv', dtype=str)
    for endpoint_import in endpoint_list:
        data_source = pd.read_excel(
            io=template_file,
            engine="xlrd",
            sheet_name=f'{endpoint_import}',
            dtype=str
        )
        lookup = api_objects.loc[api_objects['endpoint']
                                 == endpoint_import, 'lookup'].item()
        lookup_list = lookup.split(",")
        data_source.fillna('', inplace=True)
        total_source = len(data_source[data_source.columns[0]])
        for i in range(total_source):
            data_temp = build_dict(data_source, i)
            lookup_temp = build_lookup(lookup_list, data_source, i)
            source_to_import['operations'].append({'lookup': lookup_temp,
                                                   'action': 'REPLACE', 'resource': f'{endpoint_import}',
                                                   'data': data_temp})
    return source_to_import
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = build_import(uploaded_file)
    st.write(bytes_data)
    st.download_button(
        label="Download json",
        data=json.dumps(bytes_data),
        file_name=f'batch-file-import.json',
        mime='text/csv',
    )
# ---SIDEBAR---


# city = df['City'].drop_duplicates()
# make_choice = st.sidebar.selectbox('Select your data:', city)
# gender = df['Gender'].loc[df["City"] == make_choice]
