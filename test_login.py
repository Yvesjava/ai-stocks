import requests

url = 'http://192.168.10.10/api/auth/login'
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'pragma': 'no-cache',
    'x-request-id': 'req_1777119011857_w8vuiracp'
}
body = '{"username":"admin","password":"admin123"}'

response = requests.post(url, headers=headers, data=body, allow_redirects=False)
print('Status Code:', response.status_code)
print('Content:', response.text)
