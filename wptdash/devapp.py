#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from wptdash.factory import create_app

basedir = os.path.abspath(os.path.dirname(__file__))

dev_app = create_app(dict(
    DEBUG=True,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_DATABASE_URI='sqlite:///%s' % os.path.join(basedir,
                                                          'data-dev.sqlite')
))

if __name__ == "__main__":
    dev_app.run()
