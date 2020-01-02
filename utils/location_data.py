# # from socket import timeout
# from urllib.error import URLError, HTTPError

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy import exc

from utils.prepared_addresses import do_reformatting_address


GEOLOCATOR = Nominatim(user_agent='test')
GEOCODE = RateLimiter(GEOLOCATOR.geocode, min_delay_seconds=1)


def get_location(address: str):
    """Отправляет адрес в сервису Nominatim и получает геоданные"""
    try:
        return GEOCODE(address).raw  # dict
    except exc.GeocoderTimedOut:
        print(f'GET_LOC: Timeout for address: {address}')
        return False
    except exc.GeocoderServiceError:
        print(f'GET_LOC: No connection')
        return False
    except AttributeError:
        print(f'GET_LOC: No result for address: {address}')
        return False


def add_data_to_dataframe(df: object, data: dict, index: int):
    """Добавляет полученные геоданные в датафрейм"""
    if check_data(data, index):
        df.lat[index] = data['lat']
        df.lon[index] = data['lon']
        df.raw_class[index] = data['class']
        df.raw_type[index] = data['type']
        print(f'ADD_DATA: Data is added for index {index}\n')
        return True
    else:
        return False


def check_data(data: dict, index: int):
    """Проверяет наличие нужных данных в ответе от сервиса Nominatim"""
    if data:
        if 'class' in data:
            if data['class'] != 'highway' and data['class'] != 'place':
                return True
            else:
                print('CHECK: The "class" is equal the "highway" or "place"')
                return False
        else:
            print('CHECK: No "class" in data')
            return False
    else:

        print(f'CHECK: No data for index: {index}')
        return False


def data_handler(df: object, index_list: list):
    """Получает на вход список индексов по которым необходимо произвести геокодирование.
    Инициируеи:
     - запрос к сервису Nominatim.
     - проверку полученных данных.
     - добавление данных в дататфрейм"""
    top = len(index_list)
    bottom = 1
    for index in index_list:
        print(f'PROCESSING: {bottom} row of {top} rows')
        bottom += 1
        data = get_location(df['prepared_address_v1'][index])
        if add_data_to_dataframe(df, data, index):
            continue
        else:
            print(f'PROCESSING: Making new address for index {index}')
            new_address = do_reformatting_address(df['prepared_address_v1'][index])
            data = get_location(new_address)
            if add_data_to_dataframe(df, data, index):
                continue
            else:
                print(f'PROCESSING: No data for index {index}')
        print('\n')

if __name__ == '__main__':
    import urllib
    print(dir(urllib.error.URLError.with_traceback))
    print(dir(urllib.error.HTTPError))


