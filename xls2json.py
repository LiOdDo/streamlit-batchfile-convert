import json
import os
import pandas as pd


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
        'G:/My Drive/ds_working_python/byoi_utility/api_objects.csv', dtype=str)
    for endpoint in endpoint_list:
        data_source = pd.read_excel(
            io=template_file,
            engine="xlrd",
            sheet_name=f'{endpoint}',
            dtype=str
        )
        lookup = api_objects.loc[api_objects['endpoint']
                                 == endpoint, 'lookup'].item()
        lookup_list = lookup.split(",")
        data_source.fillna('', inplace=True)
        total_source = len(data_source[data_source.columns[0]])
        for i in range(total_source):
            data_temp = build_dict(data_source, i)
            lookup_temp = build_lookup(lookup_list, data_source, i)
            source_to_import['operations'].append({'lookup': lookup_temp,
                                                   'action': 'REPLACE', 'resource': f'{endpoint}',
                                                   'data': data_temp})
    return source_to_import
