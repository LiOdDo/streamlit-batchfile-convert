import json
import os
import pandas as pd

# os.chdir('C:/Users/Li Li/OneDrive/Documents/python/python_playground_ws/byoi_utility')


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


def convert_csv(template_file, endpoint):
    # from .import build_dict

    data_source = pd.read_csv(template_file, dtype=str)
    data_source.fillna('', inplace=True)
    source_to_import = {"onFailure": "ABORT",
                        "operations": []}
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


def convert_contract(contract_source):
    # os.chdir(
    #    'C:/Users/Li Li/OneDrive/Documents/python/python_playground_ws/byoi_utility')

    contract_source = pd.read_csv(
        contract_source, dtype=str)

    # buiding serviceModels types body
    hourly_guarding = {
        "name": "ContractHourlyServiceModel",
        "serviceType": "HOURLY_GUARDING",
        "settings": {"include_details": "0"}
    }
    enforce_patrol = {
        "name": "ContractPatrolServiceModel",
        "serviceType": "SCHEDULED_PATROLS_ENFORCE",
        "settings": {"include_details": "0"}
    }
    ongoing_patrol = {
        "name": "ContractPatrolVisitsServiceModel",
        "serviceType": "SCHEDULED_PATROLS_ONGOING",
        "settings": {"include_details": "0"}
    }
    recurrent_fixed = {
        "name": "ContractRecurrentFixedCostServiceModel",
        "serviceType": "RECURRENT_FIXED_COST",
        "settings": {"include_details": "0"}
    }
    dispatch_service = {
        "name": "DispatchServiceModel",
        "serviceType": "DISPATCH_SERVICE",
        "settings": {"include_details": "0"}
    }

    # building the Contract to import json file body
    contract_to_import = {"onFailure": "ABORT",
                          "operations": []}
    total_contracts = len(contract_source['site uid'])

    for i in range(total_contracts):
        data_temp = {
            "account": {"customId": contract_source['site uid'][i]},
            "customId": contract_source['Code/ID'][i],
            "billingFrequency": contract_source['Billing Recurrence'][i],
            "billingFrequencyType": contract_source['Billing Type'][i],
            "billingStartDate": contract_source['Service Start Date'][i],
            "semiMonthlyFirstReferenceDay": "-1",
            "semiMonthlySecondReferenceDay": "-1",
            "invoiceDayToAdd": 0,
            "name": contract_source['Contract Label'][i],
            "paymentMethod": contract_source['Payment Method'][i],
            "paymentTerms": contract_source['Payment Terms'][i],
            "serviceEndDate": '',
            "serviceStartDate": contract_source['Service Start Date'][i],
            "type": "CONTRACT"
        }
        ServiceModels = []
        if contract_source['Service Type: Hourly Guarding'][i] == 'TRUE':
            ServiceModels.append(hourly_guarding)
        if contract_source['Service Type: Scheduled Patrols (Enforce Service Periods)'][i] == 'TRUE':
            ServiceModels.append(enforce_patrol)
        if contract_source['Service Type: Scheduled Patrols (Ongoing Services)'][i] == 'TRUE':
            ServiceModels.append(ongoing_patrol)
        if contract_source['Service Type: Recurrent Fixed Cost Model'][i] == 'TRUE':
            ServiceModels.append(recurrent_fixed)
        if contract_source['Service Type: Dispatch Service Model'][i] == 'TRUE':
            ServiceModels.append(dispatch_service)

        data_temp["contractServiceModels"] = ServiceModels

        # data_temp["customId"] = contract_source['Code / ID'][i]
        # data_temp["account"] = contract_source['TT site id (PSE Portal)'][i]
        # data_temp["name"] = contract_source['Contract Label'][i]
        contract_to_import['operations'].append({'lookup': {'account.customId': contract_source['site uid'][i],
                                                            'name': contract_source['Contract Label'][i]},
                                                 'action': 'REPLACE',
                                                 'resource': 'contracts',
                                                 'data': data_temp})

    # writing the file to contract_to_import.json
    with open('contract_to_import.json', 'w') as outfile:
        json.dump(contract_to_import, outfile)


def convert_site(site_source):
    # os.chdir(
    #    'C:/Users/Li Li/OneDrive/Documents/python/python_playground_ws/byoi_utility')

    client_source = pd.read_csv(site_source, dtype=str)
    client_source.fillna('', inplace=True)
    client_to_import = {"onFailure": "ABORT",
                        "operations": []}
    total_clients = len(client_source['region'])

    for i in range(total_clients):
        region = client_source['region'][i][client_source['region'][i].find(
            "[[")+2:client_source['region'][i].find("]]")]
        # state = client_source['state'][i][client_source['state'][i].find("[[")+2:client_source['state'][i].find("]]")]
        data_temp = {
            "region": f'{region}',
            "customId": client_source['site_id'][i],
            "company": client_source['*company'][i],
            "type": "MULTI_LOCATION_CLIENT",
            "firstName": client_source['first_name'][i],
            "lastName": client_source['last_name'][i],
            "primaryPhone": client_source['phone_main'][i],
            "secondaryPhone": client_source['phone_other'][i],
            "email": client_source['email'][i],
            "address": {
                    "addressLine1": client_source['*address'][i],
                    "city": client_source['*city'][i],
                "state": ' ',
                "country": ' ',
                "postalCode": client_source['zip'][i]
            }
        }
        if "[[" in client_source['state'][i]:
            state_value = client_source['state'][i][client_source['state'][i].find(
                "[[")+2:client_source['state'][i].find("]]")]
            data_temp["address"]["state"] = state_value
        if "[[" not in client_source['state'][i] and client_source['state'][i] != '':
            data_temp["address"]["state"] = client_source['state'][i]
        if "[[" in client_source['*country'][i]:
            country_value = client_source['*country'][i][client_source['*country'][i].find(
                "[[")+2:client_source['*country'][i].find("]]")]
            data_temp["address"]["country"] = country_value
        if "[[" not in client_source['*country'][i] and client_source['*country'][i] != '':
            data_temp["address"]["country"] = client_source['*country'][i]

        client_to_import['operations'].append({'lookup': {'region': f'{region}', 'customId': client_source['site_id'][i], "company": client_source['*company'][i]},
                                               'action': 'REPLACE', 'resource': 'clients',
                                               'data': data_temp})

    with open('client_to_import.json', 'w') as outfile:
        json.dump(client_to_import, outfile)
