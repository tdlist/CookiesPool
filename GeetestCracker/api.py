# -*- coding: utf-8 -*-
# @Time    : 2019/9/7 15:17
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : api.py
# @Software: PyCharm

from gevent import monkey
monkey.patch_all()

import threading
import base64
from flask import Flask, abort, jsonify, request, send_from_directory
from gevent.pywsgi import WSGIServer
from uuid import uuid4
from GeetestCracker.cracker2 import Cracker


app = Flask(__name__)

cv_put = threading.Condition()
cv_get = threading.Condition()

workers = 0

tasks = {}
pending = []
doing = []
done = []


def main(address="0.0.0.0", port=8778):
    http_server = WSGIServer((address, port), app)
    http_server.serve_forever()


@app.route("/")
def root():
    return f"<html><head><title>Geetest3 - Status</title><meta http-equiv=\"refresh\" content=\"5\"></head><body>Geetest3 Distributed Cracking Platform<br /><a href=\"https://github.com/Hsury/Geetest3-Crack\">https://github.com/Hsury/Geetest3-Crack</a><br /><br />Workers: {workers + len(doing)}<br /><br />Pending: {len(pending)}<br />Doing: {len(doing)}<br />Done: {len(done)}</body></html>"


@app.route("/crack3", methods=['POST'])
def crack3():
    if all([key in request.form for key in {'gt', 'challenge'}]):
        session = str(uuid4())
        tasks[session] = {
            'code': -1,
            'gt': request.form.get('gt'),
            'challenge': request.form.get('challenge'),
            'success': request.form.get('success', 1),
            'validate': "",
            'seccode': "",
        }
        pending.append(session)
        with cv_put:
            cv_put.notify_all()
        with cv_get:
            if cv_get.wait_for(lambda: session in done, timeout=30):
                # done.remove(session)
                if tasks[session]['code'] == 0:
                    return jsonify({
                        'code': 0,
                        'message': "success",
                        'challenge': tasks[session]['challenge'],
                        'validate': tasks[session]['validate'],
                        'seccode': tasks[session]['seccode'],
                    })
                else:
                    return jsonify({
                        'code': -2,
                        'message': "forbidden",
                    })
            else:
                if session in pending:
                    pending.remove(session)
                if session in doing:
                    doing.remove(session)
                done.append(session)
                return jsonify({
                    'code': -3,
                    'message': "timeout",
                })
        del tasks[session]
    else:
        return jsonify({
            'code': -1,
            'message': "invalid parameter",
        })


@app.route("/crack2", methods=['POST'])
def crack2():
    if all([key in request.form for key in {'referer', 'gt', 'challenge'}]):
        referer = base64.b64decode(request.form.get('referer')).decode()
        result = Cracker(referer, request.form.get('gt'), request.form.get('challenge')).run()
        if result['data']['success']:
            return jsonify({
                'code': 0,
                'message': "success",
                'challenge': result['challenge'],
                'validate': result['data']['validate'],
                'seccode': "{}|jordan".format(result['data']['validate']),
            })
        else:
            return jsonify({
                'code': -2,
                'message': "forbidden",
            })
    else:
        return jsonify({
            'code': -1,
            'message': "invalid parameter",
        })


@app.route('/favicon.ico')
def favicon():
    return send_from_directory("static", "favicon.ico", mimetype="image/vnd.microsoft.icon")


@app.route("/feedback", methods=['POST'])
def feedback():
    if all([key in request.form for key in ['session', 'code']]):
        session = request.form.get('session')
        if session in doing:
            if request.form.get('code') == "0" and all([key in request.form for key in ['challenge', 'validate', 'seccode']]):
                tasks[session]['code'] = 0
                tasks[session]['challenge'] = request.form.get('challenge')
                tasks[session]['validate'] = request.form.get('validate')
                tasks[session]['seccode'] = request.form.get('seccode')
            doing.remove(session)
            done.append(session)
            with cv_get:
                cv_get.notify_all()
            return jsonify({
                'code': 0,
                'message': "success",
            })
        else:
            return jsonify({
                'code': -2,
                'message': "invalid session",
            })
    else:
        return jsonify({
            'code': -1,
            'message': "invalid parameter",
        })


@app.route("/fetch")
def fetch():
    global workers
    workers += 1
    with cv_put:
        if cv_put.wait_for(lambda: pending, timeout=15):
            session = pending.pop(0)
            doing.append(session)
            workers -= 1
            return jsonify({
                'session': session,
                'gt': tasks[session]['gt'],
                'challenge': tasks[session]['challenge'],
                'success': tasks[session]['success'],
            })
        else:
            workers -= 1
            abort(503)


@app.route("/status")
def status():
    return jsonify({
        'code': 0,
        'workers': workers + len(doing),
        'pending': len(pending),
        'doing': len(doing),
        'done': len(done),
    })


@app.route("/task")
def task():
    return app.send_static_file("geetest.html")


if __name__ == "__main__":
    main()

