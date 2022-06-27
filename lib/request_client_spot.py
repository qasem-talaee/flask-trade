import hashlib
import requests
import time

class RequestClient(object):
    
    def __init__(self, access_id, secret_key):
        self.headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
        }
        self.access_id = access_id
        self.secret_key = secret_key
        self.host = "https://api.coinex.com/v1"
        
    def get_sign(self, params):
        sort_params = sorted(params)
        data = []
        for item in sort_params:
            data.append(item + '=' + str(params[item]))
        str_params = "{0}&secret_key={1}".format('&'.join(data), self.secret_key)
        token = hashlib.md5(str_params.encode()).hexdigest().upper()
        return token
        
    def get_auth(self, params):
        params['access_id'] = self.access_id
        self.headers['authorization'] = self.get_sign(params)
        
    def get(self, path, params=None, sign=True):
        url = self.host + path
        params = params or {}
        params['tonce'] = int(time.time()*1000)
        if sign:
            self.get_auth(params)
        response = requests.get(url, params=params, headers=self.headers)
        if response.status_code == requests.codes.ok:
            if response.json()['code'] == 0:
                return response.json()
            else:
                print('Try again')
        else:
            print('Try again')

    def post(self, path, data=None):
        url = self.host + path
        data = data or {}
        data['tonce'] = int(time.time()*1000)
        self.get_auth(data)
        response = requests.post(url, headers=self.headers, params=data)
        if response.status_code == requests.codes.ok:
            if response.json()['code'] == 0:
                return response.json()
            else:
                print('Try again')
        else:
            print('Try again')