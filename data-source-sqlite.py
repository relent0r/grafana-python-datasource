import math
import sqlite3

from datetime import datetime
from calendar import timegm
from bottle import (Bottle, HTTPResponse, run, request, response,
                    json_dumps as dumps)

app = Bottle()


def convert_to_time_unixepoch(timestamp):
    return timegm(
            datetime.strptime(
                timestamp, '%Y-%m-%dT%H:%M:%S.%fZ').timetuple())

def get_all_rows(max_points):
    conn = sqlite3.connect("all.db") 
    sql = "select date, users from tracking"
    result = conn.execute(sql).fetchmany(max_points)
    conn.close()
    return result


def create_data_points(start, end, max_points):
    start = convert_to_time_unixepoch(start)
    end = convert_to_time_unixepoch(end)
    conn = sqlite3.connect("../all.db") 
    sql = "select users, unixepoch*1000 from tracking where unixepoch > ? and unixepoch < ?"
    result = conn.execute(sql, (start, end)).fetchmany(max_points)
    conn.close()
    return result


@app.hook('after_request')
def enable_cors():
    print("after_request hook")
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = \
        'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


@app.route("/", method=['GET', 'OPTIONS'])
def index():
    return "OK"


@app.post('/search')
def search():
    return HTTPResponse(body=dumps(['users-vs-time', 'tracking-table']),
                        headers={'Content-Type': 'application/json'})


@app.post('/query')
def query():
    body = []
    request_json = request.json
    max_points = request_json["maxDataPoints"]
    if request.json['targets'][0]['type'] == 'table':
        series = request.json['targets'][0]['target']
        body = [{"columns":[{"text": "Date", "type": "text"},
                            {"text": "Number of Users", "type": "number"},
                             ],
                 "rows": get_all_rows(max_points)            
                }]
    else:
        start, end = request_json['range']['from'], request_json['range']['to']
        for target in request.json['targets']:
            name = target['target']
            datapoints = create_data_points(start, end, max_points)
            body.append({'target': name, 'datapoints': datapoints})

    body = dumps(body)
    return HTTPResponse(body=body,
                        headers={'Content-Type': 'application/json'})


if __name__ == '__main__':
    run(app=app, host='localhost', port=8091)
