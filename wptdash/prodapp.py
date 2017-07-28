#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
from wptdash.factory import create_app

CONFIG = configparser.ConfigParser()
CONFIG.readfp(open(r'config.txt'))
WPTDASH_DB = CONFIG.get('postgresql', 'WPTDASH_DB')
WPTDASH_DB_USER = CONFIG.get('postgresql', 'WPTDASH_DB_USER')
WPTDASH_DB_PASS = CONFIG.get('postgresql', 'WPTDASH_DB_PASS')
WPTDASH_DB_URI = 'postgresql://%s:%s@localhost/%s' % (WPTDASH_DB_USER,
                                                      WPTDASH_DB_PASS,
                                                      WPTDASH_DB)

prod_app = create_app(dict(
    DEBUG=False,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_DATABASE_URI=WPTDASH_DB_URI
))

if __name__ == "__main__":
    prod_app.run()
