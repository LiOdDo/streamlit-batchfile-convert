import requests
import pandas as pd
import json


def get_token(url, access):

    payload = access

    headers = {
        'Content-Type': 'application/json',
        'Cookie': 'PHPSESSID=1gtjjjlkt2cm1jr4mgp2rsodqeegifg8'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    token = response.json()['auth']['token']

    return token


def export_data(endpoint, user_pwd, url_input):
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

    token = get_token(
        f"{url_input}rest/v1/auth", user_pwd)

    payload = {}
    headers = {
        'Authorization': 'Bearer '+token,
        'Cookie': 'PHPSESSID=vqru8j08ho4oe1uaht3d6mikchqak2or'
    }

    response = requests.request(
        "GET", f"{url_input}rest/v1/batch/file?" + param_path, headers=headers, data=payload)

    data = response.json()

    df = pd.json_normalize(data=data['operations']).filter(regex='^data.')
    df.columns = df.columns.str.replace("data.", "", regex=True)

    return df


def tql_data(user_pwd, url_input, tql_query):

    token = get_token(
        f"{url_input}rest/v1/auth", user_pwd)

    payload = {}
    headers = {
        'Authorization': 'Bearer '+token,
        'Cookie': 'PHPSESSID=vqru8j08ho4oe1uaht3d6mikchqak2or'
    }

    response = requests.request(
        "GET", f"{url_input}rest/v1/tql?tql=" + tql_query, headers=headers, data=payload)

    data = response.json()

    df = pd.json_normalize(data=data['data'])

    return df


def import_data(url_input, user_pwd, file_to_import):
    token = get_token(
        f"{url_input}rest/v1/auth", user_pwd)

    payload = json.load(file_to_import)

    headers = {
        'Authorization': 'Bearer '+token,
        'Content-Type': 'application/json',
        'Cookie': 'PHPSESSID=vqru8j08ho4oe1uaht3d6mikchqak2or'
    }
    response = requests.request(
        "POST", f"{url_input}rest/v1/batch/file", headers=headers, json=payload)
    data = response.json()

    return data
