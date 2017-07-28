#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    WPTDash
    ~~~~~~~

    An application that consolidates pull request build information into
    a single GitHub comment and provides an interface for displaying
    more detailed forms of that information.
"""

import requests_cache
from flask import Flask, g
from wptdash.database import db
from werkzeug.utils import find_modules, import_string


def create_app(config=None):
    import wptdash.models as models

    app = Flask('wptdash')

    app.config.update(config or {})
    app.config.from_envvar('WPTDASH_SETTINGS', silent=True)

    requests_cache.install_cache(backend='memory', expire_after=180)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.before_request
    def before_request():
        g.db = db
        g.models = models

    register_blueprints(app)

    return app


def register_blueprints(app):
    """ Registers all blueprint modules. """
    for name in find_modules('wptdash.blueprints'):
        mod = import_string(name)
        if hasattr(mod, 'bp'):
            app.register_blueprint(mod.bp)
    return None
