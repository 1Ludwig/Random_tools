import traceback
import requests
from requests.structures import CaseInsensitiveDict

AZURE_APP_ID = "AZ_AID"
AZURE_APPROLE_SECRET = "AZ_SECRET"
SCOPE = "SCOPE"
NETBOX_TOKEN = "NTOKEN"


# Hämta token och sätt den I en variabel
def azure_token():
    url = "https://login.microsoftonline.com/0c5af91b-8314-4175-b862-37e78355a3ef/oauth2/v2.0/token"
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    data = f"client_id={AZURE_APP_ID}&client_secret={AZURE_APPROLE_SECRET}&grant_type=client_credentials&scope={SCOPE}"
    get_azure_token = requests.post(url, headers=headers, data=data)
    # print("Status code:", get_azure_token.status_code)
    return get_azure_token.json().get('access_token')


# Lägga till prefix:
def add_prefixes():
    url = "http://ipam.visolit.org/api/ipam/prefixes/"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = f"Bearer {azure_token()}"
    headers["netboxtoken"] = NETBOX_TOKEN
    headers["Content-Type"] = "application/json"
    headers["Accept"] = "application/json"
    data = '{"prefix": "190.75.50.0/24", "site": 1}'
    resp = requests.post(url, headers=headers, data=data)
    return resp


# ta bort prefix (OBS: måste specificera prefix ID):
def delete_prefixes():
    url = "http://ipam.visolit.org/api/ipam/prefixes/"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = f"Bearer {azure_token()}"
    headers["netboxtoken"] = NETBOX_TOKEN
    headers["Content-Type"] = "application/json"
    headers["Accept"] = "application/json"
    data = '[{"id": 149}]'
    resp = requests.delete(url, headers=headers, data=data)
    return resp


# ta bort prefix (OBS: måste specificera prefix ID):
def view_prefixes():
    url = "http://ipam.visolit.org/api/ipam/prefixes/"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = f"Bearer {azure_token()}"
    headers["netboxtoken"] = NETBOX_TOKEN
    headers["Content-Type"] = "application/json"
    headers["Accept"] = "application/json"
    data = '[{"vrf": 1}]'
    resp = requests.get(url, headers=headers, data=data)
    return resp



try:
    # add_prefixes()
    # delete_prefixes()
    # view_prefixes()
    function = add_prefixes()
    print(function.content)

    if function.status_code == 200:
        print("Request Successful: HTML Get request OK.")
    if function.status_code == 201:
        print("Request Successful: Prefix added")
    if function.status_code == 204:
        print("Request Successful: Prefix deleted")

except Exception:
    print(traceback.print_exc())
finally:
    print("Finito!")
