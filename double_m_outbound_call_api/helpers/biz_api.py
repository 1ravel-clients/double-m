import json
import uuid
import requests

from odoo.tools.config import config
from odoo.exceptions import ValidationError


BASE_URL_API = "https://portal.jascloud.co.id/_o"

class BizAPI(object):
    @staticmethod
    def get_api_key():
        api_key = config.misc.get("biz_api", {}).get("api_key")
        if not api_key:
            raise ValidationError('API key is missing. Please configure API key in config file')
        return api_key

    @staticmethod
    def get_idempotency_key():
        return str(uuid.uuid4())

    @staticmethod
    def send_request(method, endpoint, data=None, querystring={}):
        headers = {'accept': 'application/json'}
        if data:
            headers['content-type'] = "application/json"

        # API key
        querystring['secret'] = BizAPI.get_api_key()

        url = BASE_URL_API + endpoint
        req = requests.request(method=method, url=url, data=data, headers=headers, params=querystring)

        if not req.status_code == requests.codes.ok:
            raise ValidationError(f"API return a non-successful code - {req.status_code} - {req.text}")

    @staticmethod
    def make_call(phone, ext):
        idempotencyKey = BizAPI.get_idempotency_key()
        data = json.dumps({
            "idempotencyKey": idempotencyKey,
            "customers": [
                {
                    "phone": phone,
                }
            ],
            "callflow": {
                "steps": [
                    {
                        "type": "dial",
                        "destination": f"$.exts['{ext}']",
                        "callerID": "$.customer.phone"
                    },
                    {
                        "type": "connect",
                        "destination": "$.customer.phone",
                        "callerID": f"$.exts['{ext}'].callerId"
                    }
                ]
            }
        })

        endpoint = '/v1/calls/'
        res = BizAPI.send_request(method='POST', endpoint=endpoint, data=data)

        return res
