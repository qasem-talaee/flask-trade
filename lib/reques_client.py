import copy
import hashlib
import requests
import time

class RequestClient(object):
    __headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
    }

    def __init__(self, access_id, secret_key):
        self.access_id = access_id
        self.secret_key = secret_key
        self.headers = self.__headers
        self.host = 'https://api.coinex.com/perpetual'

    @staticmethod
    def get_sign(params, secret_key):
        data = ['='.join([str(k), str(v)]) for k, v in params.items()]

        str_params = "{0}&secret_key={1}".format(
            '&'.join(data), secret_key).encode()

        token = hashlib.sha256(str_params).hexdigest()
        return token

    def set_authorization(self, params, headers):
        headers['AccessId'] = self.access_id
        headers['Authorization'] = self.get_sign(params, self.secret_key)

    def get(self, path, params=None, sign=True, default_path=True):
        if default_path:
            url = self.host + path
        else:
            url = path
        params = params or {}
        params['timestamp'] = int(time.time()*1000)
        headers = copy.copy(self.headers)
        if sign:
            self.set_authorization(params, headers)
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == requests.codes.ok:
            if response.json()['code'] == 0:
                return response.json()
            else:
                return 'Try again'
        else:
            return 'Try again'

    def post(self, path, data=None, default_path=True):
        if default_path:
            url = self.host + path
        else:
            url = path
        data = data or {}
        data['timestamp'] = int(time.time()*1000)
        headers = copy.copy(self.headers)
        self.set_authorization(data, headers)
        response = requests.post(url, data=data, headers=headers)
        if response.status_code == requests.codes.ok:
            if response.json()['code'] == 0:
                return response.json()
            else:
                return 'Try again'
        else:
            return 'Try again'