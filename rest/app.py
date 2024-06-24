# -*- coding: utf-8 -*-

from flask import Flask

from rest.api import log_bp  # noqa: I202

app = Flask(__name__)
app.register_blueprint(log_bp)
