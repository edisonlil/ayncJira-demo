# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
from requests.auth import HTTPBasicAuth
import json

url = "http://139.198.168.71:28080/rest/api/2/issue/createmeta"

auth = HTTPBasicAuth("admin", "Cloudlink#2022")

headers = {
  "Accept": "application/json"
}

response = requests.request(
   "GET",
   url,
   headers=headers,
   auth=auth
)

if __name__ == "__main__":
    print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))