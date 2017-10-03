#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date
import math


def get_quarter_start_date(quarter, year):
    quarter_first_month = quarter * 3 - 2
    quarter_start = date(year, quarter_first_month, 1)
    return quarter_start


def get_default_start_end():
    month_end_days = {
        3: 31,
        6: 30,
        9: 30,
        12: 31
    }
    today = date.today()
    month = today.month
    year = today.year
    quarter = math.ceil(month / 3.0)
    quarter_start = get_quarter_start_date(quarter, year)
    delta = today - quarter_start
    # If this is before the midpoint of the quarter, show the previous quarter
    # by default.
    if delta.days < 45:
        quarter -= 1
        if quarter == 0:
            quarter = 4
            year -= 1
        quarter_start = get_quarter_start_date(quarter, year)
    quarter_end_month = quarter_start.month + 2
    quarter_end = date(year, quarter_end_month,
                       month_end_days[quarter_end_month])
    return quarter_start, quarter_end
