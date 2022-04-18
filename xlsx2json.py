import json
import os
import pandas as pd
from openpyxl import load_workbook


def get_sheetnames_xlsx(filepath):
    wb = load_workbook(filepath, read_only=True, keep_links=False)
    return wb.sheetnames


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


def convert_xlsx(template_file):
    # from .import build_dict
    source_to_import = {"onFailure": "ABORT", "operations": []}
    endpoint_list = get_sheetnames_xlsx(template_file)
#    api_objects = pd.read_csv(
#        'api_objects.csv', dtype=str)
    for endpoint in endpoint_list:
        data_source = pd.read_excel(
            io=template_file,
            engine="openpyxl",
            sheet_name=f'{endpoint}',
            dtype=str
        )
        # lookup = api_objects.loc[api_objects['endpoint']
        #                          == endpoint, 'lookup'].item()
        # lookup_list = lookup.split(",")
        lookup_list = []
        for col in data_source.columns:
            if "*" in col:
                col = col.replace("*", "")
                lookup_list.append(col)

        data_source.columns = data_source.columns.str.replace("*", "")
        data_source.fillna('', inplace=True)
        total_source = len(data_source[data_source.columns[0]])
        for i in range(total_source):
            data_temp = build_dict(data_source, i)
            lookup_temp = build_lookup(lookup_list, data_source, i)
            source_to_import['operations'].append({'lookup': lookup_temp,
                                                   'action': 'REPLACE', 'resource': f'{endpoint}',
                                                   'data': data_temp})
    return source_to_import
