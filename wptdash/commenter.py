#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
import logging
import requests
from operator import attrgetter
from flask import render_template

from wptdash.github import GitHub

CONFIG = configparser.ConfigParser()
CONFIG.readfp(open(r'config.txt'))
APP_DOMAIN = CONFIG.get('app', 'APP_DOMAIN')
ORG_NAME = CONFIG.get('GitHub', 'ORG')
REPO_NAME = CONFIG.get('GitHub', 'REPO')


# TODO: make this return some useful JSON
def update_github_comment(pr):
    if pr.builds:
        github = GitHub()
        build = sorted(pr.builds, key=attrgetter('started_at'), reverse=True)[0]
        has_unstable = False
        for job in build.jobs:
            for test in job.tests:
                if not test.consistent:
                    has_unstable = True
                    break
            if has_unstable:
                break

        comment = render_template('comment.md', build=build,
                                  app_domain=APP_DOMAIN, org_name=ORG_NAME,
                                  repo_name=REPO_NAME,
                                  has_unstable=has_unstable)
        if not github.validate_comment_length(comment):
            comment = render_template('comment-short.md', build=build,
                                      app_domain=APP_DOMAIN, org_name=ORG_NAME,
                                      characters=github.max_comment_length,
                                      repo_name=REPO_NAME,
                                      has_unstable=has_unstable)
        try:
            github.post_comment(pr.number, comment)
        except requests.RequestException as err:
            logging.error(err.response.text)
            return err.response.text, 500

    return 'OK', 200
