import requests
import json
import simplekml
import time


class vehicle:
    def __init__(self, id, lat, lng, name, fuel_level):
        self.id = id
        self.lat = lat
        self.lng = lng
        self.name = name
        self.fuel_level = fuel_level
        self.sensor_num = None  # ?


class polygon:
    def __init__(self, id, lat, lng, name):
        self.id = id
        self.name = name
        self.lat = lat
        self.lng = lng


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


def get_device_ids(token, schema_id):  # возвращает список с id транспорта
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


def get_geofence_ids(token, schema_id):  # возвращает список с id геозон
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


def get_geofence_data_by_id(token, schema_id, geofence_id):  # возвращает все данные о определенной геозоне по id
    geofence_resp = requests.get('http://cloud.ckat-nn.ru/ServiceJSON/GetGeoFences?session={}&schemaID={}&IDs={}'.format(
            token, schema_id, geofence_id))
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
    polygons = list()
    for id in ids:
        if req_size == max_req_size - 1:
            ids_req_str += id + ','
            geofences = get_geofence_data_by_id(token, schema_id, ids_req_str)
            if geofences != -1:
                print('Retrieved the following geofence ids (max {} per request): {}'.format(max_req_size, ids_req_str))
                for geofence_id in geofences:
                    pg = polygon(geofence_id, geofences[geofence_id]['Lat'], geofences[geofence_id]['Lng'],
                                 geofences[geofence_id]['Name'])
                    polygons.append(pg)
            ids_req_str = ''
            req_size = 0
        else:
            ids_req_str += id + ','
            req_size += 1

    # для оставшихся
    geofences = get_geofence_data_by_id(token, schema_id, ids_req_str)
    if geofences != -1:
        print('Retrieved the following geofence ids (max {} per request): {}'.format(max_req_size, ids_req_str))
        for geofence_id in geofences:
            pg = polygon(geofence_id, geofences[geofence_id]['Lat'], geofences[geofence_id]['Lng'],
                         geofences[geofence_id]['Name'])
            polygons.append(pg)

    return polygons


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
        vehicles = list()
        for vehicle_id in online_info_all:
            if (online_info_all[vehicle_id] != None):
                if online_info_all[vehicle_id]['LastPosition']['Lat'] != 0 and online_info_all[vehicle_id]['LastPosition']['Lng'] != 0:
                    if 'FuelPercent' in online_info_all[vehicle_id]['Final']:
                        vh = vehicle(vehicle_id, online_info_all[vehicle_id]['LastPosition']['Lat'],
                                     online_info_all[vehicle_id]['LastPosition']['Lng'], online_info_all[vehicle_id]['Final']['ID_1C_f'],
                                     online_info_all[vehicle_id]['Final']['FuelPercent'])
                        vehicles.append(vh)
                        '''
                        vehicle_data[key] = online_info_all[key]['LastPosition']
                        vehicle_data[key]['FuelPercent'] = online_info_all[key]['Final']['FuelPercent']
                        vehicle_data[key]['Name'] = online_info_all[key]['Name']
                        print(online_info_all[key]['Final']['ID_1C_f'])
                        '''
                    else:
                        print('No fuel level for', vehicle_id)
                else:
                    print('No coordinates for', vehicle_id)
            else:
                print('No info about', vehicle_id)
        return vehicles
    else:
        print('GetOnlineInfoAll error')
        return -1


def add_data_to_kml(vehicles, polygons, filename):  # рисует всю технику и все геозоны на карте
    kml = simplekml.Kml()
    for vh in vehicles:
        pnt = kml.newpoint()
        pnt.name = vh.name + ' (' + str(round(vh.fuel_level)) + '%)'
        pnt.description = 'ID: ' + vh.id + '\n' + 'The fuel level is: ' + str(round(vh.fuel_level)) + '%'
        pnt.coords = [(vh.lng, vh.lat)]
    for pg in polygons:
        pol = kml.newpolygon()
        boundaries = []
        for boundary_num in range(len(pg.lat)):
            boundaries.append((pg.lng[boundary_num], pg.lat[boundary_num]))
        pol.outerboundaryis = boundaries
        pol.name = pg.name
        pol.style.polystyle.color = '80E8D300'
    kml.save(filename)


def update(token, schema_id, devices_ids, geofence_ids, refresh_time):  # обновляет kml файл через заданные промежутки времени
    flag = True
    while flag:
        vehicle_data = get_vehicle_data_all(token, schema_id)
        geofence_data = get_geofence_data_all(token, schema_id, geofence_ids)
        add_data_to_kml(vehicle_data, geofence_data, 'vehicles_and_polygons.kml')
        time.sleep(refresh_time)


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
    devices_ids = get_device_ids(token, schema_id)
    print(devices_ids)
    geofence_ids = get_geofence_ids(token, schema_id)
    print(geofence_ids)

    update(token, schema_id, devices_ids, geofence_ids, 60)  # обновляем каждые 60 секунд
    