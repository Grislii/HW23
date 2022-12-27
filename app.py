import os

from flask import Flask, request, jsonify
from flask_restx import Resource, Namespace, Api
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

perform_query_ns = Namespace("perform_query")
do_query_ns = Namespace("do_query")

api = Api(app)
api.add_namespace(perform_query_ns)
api.add_namespace(do_query_ns)

def do_cmd(cmd, value, data):
    if cmd == 'filter':
        result = list(filter(lambda record: value in record, data))
    elif cmd == 'map':
        col_num = int(value)
        result = list(map(lambda record: record.split()[col_num], data))
    elif cmd == 'unique':
        result = list(set(data))
    elif cmd == 'sort':
        reverse = value == 'desc'
        result = sorted(data, reverse=reverse)
    elif cmd == 'limit':
        col_num = int(value)
        result = [line for line in list(data)[:col_num]]
    return result


def do_query(params):
    with open(os.path.join(DATA_DIR, params["file_name"])) as file:
        file_data = file.readlines()

    res = file_data

    num = 1
    cmd = 'cmd' + str(num)
    value = 'value' + str(num)
    print(params.keys())

    while cmd in params.keys() and value in params.keys():
        if cmd in params.keys():
            res = do_cmd(params[cmd], params[value], res)
        cmd = 'cmd' + str(num)
        value = 'value' + str(num)
        num += 1

    return res


@perform_query_ns.route('/')
class PerformQuery(Resource):
    def post(self):
        rq_json = request.json

        filename = rq_json["file_name"]

        if not os.path.exists(os.path.join(DATA_DIR, filename)):
            raise BadRequest

        return jsonify(do_query(rq_json))


if __name__ == "__main__":
    app.run()
