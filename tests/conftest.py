#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pytest

from wptdash.factory import create_app
from wptdash.database import db as _db

basedir = os.path.abspath(os.path.dirname(__file__))

TESTDB_PATH = os.path.join(basedir, 'data-test.sqlite')
TEST_DATABASE_URI = 'sqlite:///' + TESTDB_PATH


@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    app = create_app(dict(
        DEBUG=True,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_DATABASE_URI=TEST_DATABASE_URI
    ))

    # Establish an application context before running the tests.
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def client(app, request):
    """Session-wide Flask test client."""
    client = app.test_client()
    return client


@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""
    if os.path.exists(TESTDB_PATH):
        os.unlink(TESTDB_PATH)

    def teardown():
        _db.drop_all()
        os.unlink(TESTDB_PATH)

    _db.app = app
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session
