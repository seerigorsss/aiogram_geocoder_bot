import requests


def static_maps(cords, map_type):
    url = "https://static-maps.yandex.ru/1.x/"
    params = {
        "ll": cords,
        "l": map_type,
        "spn": ",".join(["0.05", "0.05"]),
        "pt": ",".join([cords, "pm2rdm"])
    }
    response = requests.get(url, params=params)
    return response.url


def geocode_object(name):
    toponym_to_find = name

    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": toponym_to_find,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    try:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        toponym_coordinates = ",".join(toponym["Point"]["pos"].split())
        return {"OK": toponym_coordinates}
    except IndexError:
        return {"error": f'Запрос <i>{name}</i> не был обработан.\n'
                         f'Попробуйте еще раз.\n'}
