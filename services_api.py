import requests
import pandas as pd
import json
import streamlit as st
import time


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


def tql_data(token, url_input, tql_query):

    #    token = get_token(
    #        f"{url_input}rest/v1/auth", user_pwd)

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


'''
def tql_table(self):

    with st.form("TQL1", clear_on_submit=True):
        TQL_Table_1 = st.text_area("enter tql1")

        submit = st.form_submit_button("run tql1")
    with st.form("TQL2", clear_on_submit=True):
        TQL_Table_2 = st.text_area("enter tql2")

        submit = st.form_submit_button("run tql2")
    with st.form("TQL3", clear_on_submit=True):
        TQL_Table_3 = st.text_area("enter tql3")

        submit = st.form_submit_button("run tql3")
'''


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


def single_report_export(token, url_input, report_template, accounts, start_date, end_date):
    if report_template is not None:
        if len(accounts) > 0:
            url = url_input + "rest/v1/tql?tql=SELECT report,report.account.name,report.reportDateTime,report.createdBy.name,report.reportTemplate.name,templateField.label,value FROM report_fields where report.account:in=" + f"({accounts})" + \
                " AND report.reportTemplate =" + report_template + " AND date(report.reportDateTime) >= '" + f"{start_date}" + \
                "' AND date(report.reportDateTime) <= '" + \
                f"{end_date}" + "' limit 200000000"
        if len(accounts) == 0:
            url = url_input + "rest/v1/tql?tql=SELECT report,report.account.name,report.reportDateTime,report.createdBy.name,report.reportTemplate.name,templateField.label,value FROM report_fields " + \
                " WHERE report.reportTemplate =" + report_template + " AND date(report.reportDateTime) >= '" + f"{start_date}" + \
                "' AND date(report.reportDateTime) <= '" + \
                f"{end_date}" + "' limit 200000000"
        # " AND report.reportDateTime >= LAST_YEAR_START limit 20000000"
        payload = {}
        headers = {
            'Authorization': 'Bearer '+token,
            # 'Cookie': 'PHPSESSID=vqru8j08ho4oe1uaht3d6mikchqak2or',
            # 'Content-Type': 'application/json'
            'Content-Type': 'application/json; charset=utf-8'
        }

        st.text(url)
        st.text(len(accounts))

        response = requests.request(
            "GET", url, headers=headers, data=payload)

        data = response.json()
        time.sleep(2)
        df0 = pd.json_normalize(data['data'])
        # print(df)

        df1 = df0[['report', 'report.account.name', 'report.reportDateTime', 'report.createdBy.name',
                   'report.reportTemplate.name', 'templateField.label', 'value']]
        df1 = df1.rename(columns={'report': 'report id', 'report.account.name': 'account name', 'report.reportDateTime': 'report time', 'report.createdBy.name': 'reported by',
                                  'report.reportTemplate.name': 'report template', 'templateField.label': 'report field', 'value': 'reported value'})

        df_new = pd.pivot_table(df1, index=['report id', 'account name', 'report time', 'reported by', 'report template'],
                                columns=['report field'], values=['reported value'], aggfunc='first')
        df_new.to_csv(
            f'report_{report_template}.csv', sep=',', encoding='utf-8-sig')
        with open(f"report_{report_template}.csv", newline='', encoding='utf-8') as file:
            st.download_button(
                label="download this report",
                data=file,
                file_name=f"report_{report_template}.csv",
                mime="text/csv"
            )


def batch_report_export(token, url_input, report_metric_file):
    report_template = pd.read_csv(report_metric_file, dtype=str)

    temp_id = report_template['report.reportTemplate.id']
    temp_name = report_template['report.reportTemplate.name']
    account_id = report_template['report.account']
    account_name = report_template['report.account.name']

    min_id = report_template['min_id']
    max_id = report_template['max_id']

    for i in range(len(temp_id)):
        url = url_input + "rest/v1/tql?tql=SELECT report,report.account.name,report.reportDateTime,report.createdBy.name,report.reportTemplate.name,templateField.label,value FROM report_fields where report.account=" + account_id[i] + \
            " AND report.reportTemplate =" + \
            temp_id[i] + " AND report >= " + min_id[i] + \
            " AND report <=" + max_id[i] + " limit 200000000"
        # " AND report.reportDateTime >= LAST_YEAR_START limit 20000000"
        payload = {}
        headers = {
            'Authorization': 'Bearer '+token,
            # 'Cookie': 'PHPSESSID=vqru8j08ho4oe1uaht3d6mikchqak2or',
            # 'Content-Type': 'application/json'
            'Content-Type': 'application/json; charset=utf-8'
        }

        response = requests.request(
            "GET", url, headers=headers, data=payload)

        data = response.json()
        time.sleep(2)
        df0 = pd.json_normalize(data['data'])
        # print(df)

        df1 = df0[['report', 'report.account.name', 'report.reportDateTime', 'report.createdBy.name',
                   'report.reportTemplate.name', 'templateField.label', 'value']]
        df1 = df1.rename(columns={'report': 'report id', 'report.account.name': 'account name', 'report.reportDateTime': 'report time', 'report.createdBy.name': 'reported by',
                                  'report.reportTemplate.name': 'report template', 'templateField.label': 'report field', 'value': 'reported value'})

        df_new = pd.pivot_table(df1, index=['report id', 'account name', 'report time', 'reported by', 'report template'],
                                columns=['report field'], values=['reported value'], aggfunc='first')
        df_new.to_csv(
            f'report_{temp_name[i]}_{temp_id[i]}_{account_name[i]}.csv', sep=',', encoding='utf-8-sig')
        with open(f"report_{temp_name[i]}_{temp_id[i]}_{account_name[i]}.csv", newline='', encoding='utf-8') as file:
            st.download_button(
                label="download this report",
                data=file,
                file_name=f"report_{temp_name[i]}_{temp_id[i]}_{account_name[i]}.csv",
                mime="text/csv"
            )
