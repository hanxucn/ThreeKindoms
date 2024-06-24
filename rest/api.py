# -*- coding: utf-8 -*-
import os
import json  # noqa: I100
from StringIO import StringIO as BytesIO
import uuid

from flask import abort, Blueprint, request, Response


log_bp = Blueprint("api.v2.logs", "api_v2_logs", url_prefix="/api/v2")

LOG_PATH = "/usr/share/smartx/log_collector/logs/"
METADATA_PATH = "/usr/share/smartx/log_collector/metadata/"


def wrap_response(data={}, ec="EOK", error={}):
    return {"data": data, "ec": ec, "error": error}


def _get_current_node_log():
    metadata = []
    for metadata_file in os.listdir(METADATA_PATH):  # noqa: A001
        with open(METADATA_PATH + str(metadata_file)) as f:
            try:
                json_obj = json.load(f)
            except ValueError:
                pass
            else:
                metadata.append(json_obj)
    return metadata


@log_bp.route("/logs/node/get_current_log", methods=["GET"])
def get_current_node_log():
    metadata_info = _get_current_node_log()
    return json.dumps(wrap_response(data=metadata_info))
