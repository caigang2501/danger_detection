import sys,os
sys.path.append(os.getcwd())

from flask import request, jsonify,Blueprint
import main
import logging

bp = Blueprint("main", __name__)


@bp.route("/detect", methods=['POST'])
def mid_long_year():
    print(request.get_json())
    url = request.get_json()['path']
    points = request.get_json()['points']
    frame_interval = request.get_json()['frame_interval']
    sub_amount = request.get_json()['process_frame_count']
    result = main.main(url,points,frame_interval,sub_amount)
    return jsonify(result)

@bp.route("/addFace", methods=['POST'])
def add_face():
    url = request.get_json()['path']
    result = main.add_face(url)
    return jsonify(result)

@bp.route("/removeFace", methods=['POST'])
def remove_face():
    name = request.get_json()['name']
    result = main.remove_face(name)
    return jsonify(result)

@bp.route("/allFace", methods=['GET'])
def all_face():
    result = main.all_face()
    return jsonify(result)

@bp.route("/test", methods=['GET'])
def test():
    result = 0.1
    return jsonify(result)
