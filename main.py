import requests
import json

login = 'Весна'
password = '911912913'
log_resp = requests.get('http://cloud.ckat-nn.ru/ServiceJSON/Login?UserName={}&Password={}'.format(login, password))

if log_resp:
    print('Successfully logged in, {}'.format(log_resp.status_code))
    token = log_resp.text
    schemas_resp = requests.get('http://cloud.ckat-nn.ru/ServiceJSON/EnumSchemas?session={}'.format(token))
    schemas = schemas_resp.json()
    schema_id = schemas[0]['ID']
    print('Schema ID:', schema_id)
    print('Sсhema name:', schemas[0]['Name'])

    devices_resp = requests.get('http://cloud.ckat-nn.ru/ServiceJSON/EnumDevices?session={}&schemaID={}'.format(
        token, schema_id
    ))
    devices = devices_resp.json()
    # Далее парсим
    devices_id = []
    devices_req_str = ''
    for device in devices['Items']:
        devices_id.append(device['ID'])
        devices_req_str += device['ID'] + ','

    devices_req_str = devices_req_str[0:len(devices_req_str) - 1]  # избавляемся от последней запятой
    print(devices_req_str)

    # online_info_resp = requests.get('http://cloud.ckat-nn.ru/ServiceJSON/GetOnlineInfo?session={}&schemaID={}&IDs={}'.format(
    #    token, schema_id, devices_req_str))

    online_info_resp = requests.get('http://cloud.ckat-nn.ru/ServiceJSON/GetOnlineInfo?session={}&schemaID={}&IDs={}'.format(
        token, schema_id, devices_req_str))

    print(online_info_resp)  # почему-то выдает ошибку 500
else:
    print('An error when logging in {} has occurred'.format(log_resp.status_code))
