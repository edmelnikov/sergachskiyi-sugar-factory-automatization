import requests
import json
import simplekml


def get_token(login, password):  # возвращает токен по логину и паролю
    log_resp = requests.get('http://cloud.ckat-nn.ru/ServiceJSON/Login?UserName={}&Password={}'.format(login, password))
    if log_resp:
        token = log_resp.text
        return token
    else:
        print('Login error')
        return -1


def get_schemas(token):  # возвращает id схемы
    schemas_resp = requests.get('http://cloud.ckat-nn.ru/ServiceJSON/EnumSchemas?session={}'.format(token))
    if schemas_resp:
        schemas = schemas_resp.json()
        return schemas
    else:
        print('EnumSchemas error')
        return -1


def get_devices_id(token, schema_id):  # возвращает список с id транспорта
    devices_resp = requests.get('http://cloud.ckat-nn.ru/ServiceJSON/EnumDevices?session={}&schemaID={}'.format(
        token, schema_id))
    if devices_resp:
        devices = devices_resp.json()
        devices_id = []
        for device in devices['Items']:
            devices_id.append(device['ID'])
        return devices_id
    else:
        print('EnumDevices error')
        return -1


def get_geofences_id(token, schema_id):  # возвращает список с id геозон
    geofences_resp = requests.get('http://cloud.ckat-nn.ru/ServiceJSON/EnumGeoFences?session={}&schemaID={}'.format(token, schema_id))
    if geofences_resp:
        geofences = geofences_resp.json()
        geofences_id = []
        for geofence in geofences['Items']:
            geofences_id.append(geofence['ID'])
        return geofences_id
    else:
        print('EnumGeoFences error')
        return -1


def get_vehicle_data_by_id(token, schema_id, device_id):  # возвращает все данные о определенной единице транспорта по id
    online_info_resp = requests.get('http://cloud.ckat-nn.ru/ServiceJSON/GetOnlineInfo?session={}&schemaID={}&IDs={}'.format(
            token, schema_id, device_id))
    if online_info_resp:
        online_info_resp = online_info_resp.json()
        return online_info_resp
    else:
        print('GetOnlineInfo error')
        return -1


def get_geofence_data_by_id(token, schema_id, device_id):  # возвращает все данные о определенной геозоне по id
    geofence_resp = requests.get('http://cloud.ckat-nn.ru/ServiceJSON/GetGeoFences?session={}&schemaID={}&IDs={}'.format(
            token, schema_id, device_id))
    if geofence_resp:
        geofence_resp = geofence_resp.json()
        return geofence_resp
    else:
        print('GetGeoFences error')
        return -1


def get_geofence_data_all(token, schema_id, ids):  # возвращает координаты и название всех переданных геозон
    max_req_size = 50  # максимальное количество id, которое подается на сервер при одном запросе
    req_size = 0
    ids_req_str = ''
    geofence_data_par = dict()
    for id in ids:
        if req_size == max_req_size - 1:
            ids_req_str += id + ','
            geofence = get_geofence_data_by_id(token, schema_id, ids_req_str)
            if geofence != -1:
                print('Retrieved the following geofence ids (max {} per request): {}'.format(max_req_size, ids_req_str))
                for key in geofence:
                    geofence_data_par[key] = dict()
                    geofence_data_par[key]['Lat'] = geofence[key]['Lat']
                    geofence_data_par[key]['Lng'] = geofence[key]['Lng']
                    geofence_data_par[key]['Name'] = geofence[key]['Name']
            ids_req_str = ''
            req_size = 0
        else:
            ids_req_str += id + ','
            req_size += 1

    # для оставшихся
    geofence = get_geofence_data_by_id(token, schema_id, ids_req_str)
    if geofence != -1:
        print('Retrieved the following geofence ids (max {} per request): {}'.format(max_req_size, ids_req_str))
        for key in geofence:
            geofence_data_par[key] = dict()
            geofence_data_par[key]['Lat'] = geofence[key]['Lat']
            geofence_data_par[key]['Lng'] = geofence[key]['Lng']
            geofence_data_par[key]['Name'] = geofence[key]['Name']

    return geofence_data_par


'''
def get_vehicle_data_all(token, schema_id, all_ids):  # эта штука тоже должна была возвращать координаты техники, однако
# затем был найден более простой для этого метод (функция ниже)

    max_req_size = 50  # максимальное количество id, которое подается на сервер при одном запросе
    req_size = 0
    ids_req_str = ''
    data_all = dict()
    for id in all_ids:
        if req_size == max_req_size - 1:
            ids_req_str += id + ','
            online_info = get_vehicle_data_by_id(token, schema_id, ids_req_str)
            if online_info != -1:
                print('Retrieved the following vehicle ids (max {} per request): {}'.format(max_req_size, ids_req_str))
                for key in online_info:
                    if (online_info[key] != None):
                        if online_info[key]['LastPosition']['Lat'] != 0 and online_info[key]['LastPosition']['Lng'] != 0:
                            data_all[key] = online_info[key]['LastPosition']
                        else:
                            print('No coordinates for', key)
                    else:
                        print('No info about', key)
            ids_req_str = ''
            req_size = 0
        else:
            ids_req_str += id + ','
            req_size += 1

    # для оставшихся
    online_info_resp = requests.get(
        'http://cloud.ckat-nn.ru/ServiceJSON/GetOnlineInfo?session={}&schemaID={}&IDs={}'.format(
            token, schema_id, ids_req_str))
    online_info = online_info_resp.json()
    if online_info != -1:
        print('Retrieved the following ids (max {} per request): {}'.format(max_req_size, ids_req_str))
        for key in online_info:
            if (online_info[key] != None):
                if online_info[key]['LastPosition']['Lat'] != 0 and online_info[key]['LastPosition']['Lng'] != 0:
                    data_all[key] = online_info[key]['LastPosition']
                else:
                    print('No coordinates for', key)
            else:
                print('No info about', key)

    return data_all
'''


def get_vehicle_data_all(token, schema_id):  # возвращает имя, координаты и остаток топлива в процентах для всех единиц техники
    online_info_all_resp = requests.get('http://cloud.ckat-nn.ru/ServiceJSON/GetOnlineInfoAll?session={}&schemaID={}'.format(token, schema_id))
    if online_info_all_resp:
        online_info_all = online_info_all_resp.json()
        vehicle_data = dict()
        for key in online_info_all:
            if (online_info_all[key] != None):
                if online_info_all[key]['LastPosition']['Lat'] != 0 and online_info_all[key]['LastPosition']['Lng'] != 0:
                    if 'FuelPercent' in online_info_all[key]['Final']:
                        vehicle_data[key] = online_info_all[key]['LastPosition']
                        vehicle_data[key]['FuelPercent'] = online_info_all[key]['Final']['FuelPercent']
                        vehicle_data[key]['Name'] = online_info_all[key]['Name']
                    else:
                        print('No fuel level for', key)
                else:
                    print('No coordinates for', key)
            else:
                print('No info about', key)
        return vehicle_data
    else:
        print('GetOnlineInfoAll error')
        return -1


def add_data_to_kml(vehicle_data, polygon_data, filename):  # рисует всю технику и все геозоны на карте
    kml = simplekml.Kml()
    for key in vehicle_data:
        pnt = kml.newpoint()
        pnt.name = vehicle_data[key]['Name'] + ' (' + str(round(vehicle_data[key]['FuelPercent'])) + '%)'
        pnt.description = 'ID: ' + key + '\n' + 'The fuel level is: ' + str(round(vehicle_data[key]['FuelPercent'])) + '%'
        pnt.coords = [(
            vehicle_data[key]['Lng'],
            vehicle_data[key]['Lat']
        )]
    for key in polygon_data:
        pol = kml.newpolygon()
        boundaries = []
        for boundary_num in range(len(polygon_data[key]['Lat'])):
            boundaries.append((polygon_data[key]['Lng'][boundary_num], polygon_data[key]['Lat'][boundary_num]))
        pol.outerboundaryis = boundaries
        pol.name = polygon_data[key]['Name']
    kml.save(filename)


# ------------------------------------------------------------------#
login = 'Весна'
password = '912912913'
# token = GetToken(login, password)
token = '49FE5BA414AD84FACBD27EAA845EA440B7638E634CD265C09FAFB45B1121D06A'
if token != -1:
    schemas = get_schemas(token)
    schema_id = schemas[0]['ID']
    print('Token:', token)
    print('Schema ID:', schema_id)
    print('Sсhema name:', schemas[0]['Name'])
    devices_ids = get_devices_id(token, schema_id)
    print(devices_ids)
    vehicle_data = get_vehicle_data_all(token, schema_id)
    geofence_ids = get_geofences_id(token, schema_id)
    print(geofence_ids)
    geofence_data = get_geofence_data_all(token, schema_id, geofence_ids)
    add_data_to_kml(vehicle_data, geofence_data, 'vehicles_and_polygons.kml')


    #key = '061307a6-0d83-4697-b513-46bb18030a8e'
    #data = get_vehicle_data_by_id(token, schema_id, key)

    # coordinates = data[key]['LastPosition']
    #resp = requests.get('http://cloud.ckat-nn.ru/ServiceJSON/EnumGeoFences?session={}&schemaID={}'.format(token, schema_id))
    #resp = resp.json()
    #key = '50f54a8f-1048-4c12-8dff-e7d47d714d10'
    #resp = requests.get('http://cloud.ckat-nn.ru/ServiceJSON/GetGeoFences?session={}&schemaID={}&IDs={}'.format(token, schema_id, key))
    #resp = resp.json()
    #print(resp)
    #geofence_ids = get_geofences_id(token, schema_id)
    #print(resp)
    #print(len(data))
    #print(data[key]['Name'])
    #test = get_geofence_data_by_id(token, schema_id, key)
    #print(test[key]['Name'])
    #print(test[key]['Lat'])
    #print(test[key]['Lng'])
    #test = get_geofence_data_all(token, schema_id, geofence_ids)
    #print(len(test['0b9bbf6c-3b20-44ea-b10f-c5877c444210']['Lat']))
    #print(len(test['0b9bbf6c-3b20-44ea-b10f-c5877c444210']['Lng']))