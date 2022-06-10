from flask.json import JSONEncoder as _JSONEncoder
import json
from datetime import date

response_data = {
    "data": {

    },
    "meta": {
        "msg": "",
        "status": 2000
    }
}


class JSONEncoder(_JSONEncoder):
    def default(self, o):
        if hasattr(o, 'keys') and hasattr(o, '__getitem__'):
            return dict(o)
        if isinstance(o, date):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        return json.JSONEncoder.default(self, o)
