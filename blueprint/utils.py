from flask.json import JSONEncoder as _JSONEncoder
import json
from datetime import date
from blueprint import RETCODE


class JSONEncoder(_JSONEncoder):
    def default(self, o):
        if hasattr(o, 'keys') and hasattr(o, '__getitem__'):
            return dict(o)
        if isinstance(o, date):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        return json.JSONEncoder.default(self, o)


def gen_response_data(status, msg, **data):
    response_data = dict()
    response_data['meta'] = {}
    response_data['data'] = {}
    response_data['meta']['msg'] = msg
    response_data['meta']['status'] = status
    response_data['data'] = data
    return response_data
