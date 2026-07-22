import requests
import pandas as pd
import json
import streamlit as st
import time
import base64
import os
import pickle
import os
import re
import urllib.parse



@st.cache
def get_token(url, access):

    payload = access

    headers = {
        'Content-Type': 'application/json',
        'Cookie': 'PHPSESSID=1gtjjjlkt2cm1jr4mgp2rsodqeegifg8'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    token = response.json()['auth']['token']

    return token


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


@st.cache
def export_data(endpoint, token, url_input):
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


@st.cache
def tql_data(token, url_input, tql_query):

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


@st.cache
def import_data(url_input, token, file_to_import):
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


@st.cache
def import_text(url_input, token, text_to_import):
    payload = json.loads(f'{text_to_import}')

    headers = {
        'Authorization': 'Bearer '+token,
        'Content-Type': 'application/json',
        'Cookie': 'PHPSESSID=vqru8j08ho4oe1uaht3d6mikchqak2or'
    }
    response = requests.request(
        "POST", f"{url_input}rest/v1/batch/file", headers=headers, json=payload)
    data = response.json()

    return data


def import_batch_chunk(url_input, token, chunk_data):
    """Import a single batch chunk (dict) without caching. Returns response JSON."""
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
    }
    response = requests.request(
        "POST", f"{url_input}rest/v1/batch/file",
        headers=headers, json=chunk_data
    )
    return response.json()


@st.cache
def single_report_export(token, url_input, report_template, accounts, start_date, end_date):
    if report_template is not None:
        if len(accounts) > 0:
            url = url_input + "rest/v1/tql?tql=SELECT report,report.account.name,report.reportDateTime,report.createdBy.name,report.reportTemplate.name,templateField.label,RIGH_STR(value,24) as `value0` FROM report_fields where report.account in " + f"({accounts})" + \
                " AND report.reportTemplate =" + report_template + " AND date(report.reportDateTime) >= '" + f"{start_date}" + \
                "' AND date(report.reportDateTime) <= '" + \
                f"{end_date}" + "' limit 20000"
        if len(accounts) == 0:
            url = url_input + "rest/v1/tql?tql=SELECT report,report.account.name,report.reportDateTime,report.createdBy.name,report.reportTemplate.name,templateField.label,RIGH_STR(value,24) as `value0` FROM report_fields " + \
                " WHERE report.reportTemplate =" + report_template + " AND date(report.reportDateTime) >= '" + f"{start_date}" + \
                "' AND date(report.reportDateTime) <= '" + \
                f"{end_date}" + "' limit 2000000"
        payload = {}
        headers = {
            'Authorization': 'Bearer '+token,
            'Content-Type': 'application/json; charset=utf-8'
        }

        response = requests.request(
            "GET", url, headers=headers, data=payload)

        data = response.json()
        print(data)
        time.sleep(2)
        df0 = pd.json_normalize(data['data'])
        df0

        df1 = df0[['report', 'report.account.name', 'report.reportDateTime', 'report.createdBy.name',
                   'report.reportTemplate.name', 'templateField.label', 'value0']]
        df1 = df1.rename(columns={'report': 'report id', 'report.account.name': 'account name', 'report.reportDateTime': 'report time', 'report.createdBy.name': 'reported by',
                                  'report.reportTemplate.name': 'report template', 'templateField.label': 'report field', 'value0': 'reported value'})
        df1
        df_new = pd.pivot_table(df1, index=['report id', 'account name', 'report time', 'reported by', 'report template'],
                                columns=['report field'], values=['reported value'], aggfunc='first')
        return df_new

def _safe_filename(s: str, max_len: int = 120) -> str:
    s = "" if s is None else str(s)
    s = s.strip()
    s = re.sub(r'[\\/*?:"<>|\n\r\t]+', "_", s)  # illegal filename chars
    s = re.sub(r"\s+", " ", s)
    return (s[:max_len].strip(" ._") or "file")


def _build_tql(account_id: str, template_id: str, min_id: str, max_id: str, limit: int = 200000) -> str:
    return (
        "SELECT report,report.account.name,report.reportDateTime,report.createdBy.name,"
        "report.reportTemplate.name,templateField.label,value "
        "FROM report_fields "
        f"WHERE report.account = {account_id} "
        f"AND report.reportTemplate = {template_id} "
        f"AND report >= {min_id} "
        f"AND report <= {max_id} "
        f"limit {limit}"
    )


def _extract_value_column(df0: pd.DataFrame) -> pd.Series:
    """
    Handle API returning:
      value: {type: "...", value: "..."}  -> df0["value.value"]
    Sometimes value might already be a scalar -> df0["value"]
    """
    if "value.value" in df0.columns:
        s = df0["value.value"]
    elif "value" in df0.columns:
        s = df0["value"]
    else:
        s = pd.Series([None] * len(df0))

    def _norm(x):
        if isinstance(x, (dict, list)):
            return str(x)
        return x

    return s.apply(_norm)


def _to_wide_df(rows: list) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()

    df0 = pd.json_normalize(rows)

    df = pd.DataFrame()
    df["report id"] = df0.get("report")
    df["account name"] = df0.get("report.account.name")
    df["report time"] = df0.get("report.reportDateTime")
    df["reported by"] = df0.get("report.createdBy.name")
    df["report template"] = df0.get("report.reportTemplate.name")
    df["report field"] = df0.get("templateField.label")
    df["reported value"] = _extract_value_column(df0)

    df = df.dropna(subset=["report id", "report field"], how="any")

    wide = pd.pivot_table(
        df,
        index=["report id", "account name", "report time", "reported by", "report template"],
        columns="report field",
        values="reported value",
        aggfunc="first",
    ).reset_index()

    wide.columns = [str(c) for c in wide.columns]
    return wide


@st.cache_data(ttl=3600, show_spinner=False)
def batch_report_export(token: str, url_input: str, report_metric_file: str, file_direct: str):
    """
    Batch export reports based on metric CSV.
    Creates one CSV per row and returns a result dataframe (status per row).
    """
    os.makedirs(file_direct, exist_ok=True)

    metric = pd.read_csv(report_metric_file, dtype=str).fillna("")

    required_cols = [
        "report.reportTemplate.id",
        "report.reportTemplate.name",
        "report.account",
        "report.account.name",
        "min_id",
        "max_id",
    ]
    missing = [c for c in required_cols if c not in metric.columns]
    if missing:
        raise ValueError(f"Metric file missing columns: {missing}")

    endpoint = urllib.parse.urljoin(url_input.rstrip("/") + "/", "rest/v1/tql")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
    }

    results = []

    for i, row in metric.iterrows():
        template_id = row["report.reportTemplate.id"].strip()
        template_name = row["report.reportTemplate.name"].strip()
        account_id = row["report.account"].strip()
        account_name = row["report.account.name"].strip()
        min_id = row["min_id"].strip()
        max_id = row["max_id"].strip()

        if not (template_id and account_id and min_id and max_id):
            results.append({
                "row": int(i),
                "status": "skipped",
                "reason": "missing template_id/account_id/min_id/max_id",
                "file": None,
                "rows": 0
            })
            continue

        tql = _build_tql(account_id, template_id, min_id, max_id, limit=200000)

        try:
            r = requests.get(endpoint, headers=headers, params={"tql": tql}, timeout=90)
            r.raise_for_status()
            js = r.json()
            rows = (js or {}).get("data") or []

            df_wide = _to_wide_df(rows)

            fname = f"report_{_safe_filename(template_name)}_{_safe_filename(template_id)}_{_safe_filename(account_name)}.csv"
            fpath = os.path.join(file_direct, fname)

            df_wide.to_csv(fpath, index=False, encoding="utf-8-sig")

            results.append({
                "row": int(i),
                "status": "ok",
                "reason": "",
                "file": fpath,
                "rows": int(len(df_wide)),
                "template_id": template_id,
                "account_id": account_id
            })

        except requests.HTTPError as e:
            snippet = ""
            try:
                snippet = e.response.text[:400]
            except Exception:
                pass
            results.append({
                "row": int(i),
                "status": "error",
                "reason": f"HTTP {r.status_code}: {snippet}".strip(),
                "file": None,
                "rows": 0,
                "template_id": template_id,
                "account_id": account_id
            })

        except Exception as e:
            results.append({
                "row": int(i),
                "status": "error",
                "reason": str(e),
                "file": None,
                "rows": 0,
                "template_id": template_id,
                "account_id": account_id
            })

        time.sleep(0.2)

    return pd.DataFrame(results)


'''
@st.cache
def batch_report_export(token, url_input, report_metric_file, file_direct):
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
        payload = {}
        headers = {
            'Authorization': 'Bearer '+token,
            'Content-Type': 'application/json; charset=utf-8'
        }

        response = requests.request(
            "GET", url, headers=headers, data=payload)

        data = response.json()
        time.sleep(2)
        df0 = pd.json_normalize(data['data'])

        df1 = df0[['report', 'report.account.name', 'report.reportDateTime', 'report.createdBy.name',
                   'report.reportTemplate.name', 'templateField.label', 'value']]
        df1 = df1.rename(columns={'report': 'report id', 'report.account.name': 'account name', 'report.reportDateTime': 'report time', 'report.createdBy.name': 'reported by',
                                  'report.reportTemplate.name': 'report template', 'templateField.label': 'report field', 'value': 'reported value'})

        df_new = pd.pivot_table(df1, index=['report id', 'account name', 'report time', 'reported by', 'report template'],
                                columns=['report field'], values=['reported value'], aggfunc='first')
        df_new.to_csv(
            f'{file_direct}/report_{temp_name[i]}_{temp_id[i]}_{account_name[i]}.csv', sep=',', encoding='utf-8-sig')
'''

def import_dataframe(dataframe, endpoint, action_type, url_input, token):
    # from .import build_dict
    dataframe.fillna('', inplace=True)
    source_to_import = {"onFailure": "ABORT",
                        "operations": []}
    lookup_list = []
    for col in dataframe.columns:
        if "*" in col:
            col = col.replace("*", "")
            lookup_list.append(col)

    dataframe.columns = dataframe.columns.str.replace("*", "")
    dataframe.fillna('', inplace=True)
    total_source = dataframe.shape[0]

    for i in range(total_source):
        data_temp = build_dict(dataframe, i)
        lookup_temp = build_lookup(lookup_list, dataframe, i)
        source_to_import['operations'].append({'lookup': lookup_temp,
                                               'action': f'{action_type}', 'resource': f'{endpoint}',
                                               'data': data_temp})
    payload = json.dumps(source_to_import)

    headers = {
        'Authorization': 'Bearer '+token,
        'Content-Type': 'application/json',
        'Cookie': 'PHPSESSID=vqru8j08ho4oe1uaht3d6mikchqak2or'
    }
    response = requests.request(
        "POST", f"{url_input}rest/v1/batch/file", headers=headers, json=payload)
    data = response.json()

    return data
