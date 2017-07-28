#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint
import jinja2
import json

bp = Blueprint('filters', __name__)


@jinja2.contextfilter
@bp.app_template_filter()
def fromjson(context, value):
    return json.loads(value)
