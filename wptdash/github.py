#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module contains all GitHub interaction logic."""

import configparser
import json
import logging
from urllib.parse import urljoin

import requests

CONFIG = configparser.ConfigParser()
CONFIG.readfp(open(r'config.txt'))
GH_COMMENTER = CONFIG.get('GitHub', 'GH_COMMENTER')
GH_TOKEN = CONFIG.get('GitHub', 'GH_TOKEN')
ORG = CONFIG.get('GitHub', 'ORG')
REPO = CONFIG.get('GitHub', 'REPO')


class GitHub(object):

    """Interface to GitHub API."""

    max_comment_length = 65536

    def __init__(self):
        """Create GitHub instance."""
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        self.auth = (GH_TOKEN, "x-oauth-basic")
        self.org = ORG
        self.repo = REPO
        self.base_url = "https://api.github.com/repos/%s/%s/" % (ORG, REPO)

    # default object is safe because it is not being modified
    def _headers(self, headers=None):
        """Extend existing HTTP headers and return new value."""
        if headers is None:
            headers = {}
        return_value = self.headers.copy()
        return_value.update(headers)
        return return_value

    def post(self, url, data, headers=None):
        """Serialize and POST data to given URL."""
        logging.debug("POST %s", url)
        if data is not None:
            data = json.dumps(data)
        resp = requests.post(
            url,
            data=data,
            headers=self._headers(headers),
            auth=self.auth
        )
        resp.raise_for_status()
        return resp

    def patch(self, url, data, headers=None):
        """Serialize and PATCH data to given URL."""
        logging.debug("PATCH %s", url)
        if data is not None:
            data = json.dumps(data)
        resp = requests.patch(
            url,
            data=data,
            headers=self._headers(headers),
            auth=self.auth
        )
        resp.raise_for_status()
        return resp

    def get(self, url, headers=None):
        """Execute GET request for given URL."""
        logging.debug("GET %s", url)
        resp = requests.get(
            url,
            headers=self._headers(headers),
            auth=self.auth
        )
        resp.raise_for_status()
        return resp

    def validate_comment_length(self, comment):
        return len(comment) < self.max_comment_length

    def get_pr(self, issue_number):
        """Get pull request data."""
        pr_url = urljoin(self.base_url, "pulls/%s" % issue_number)
        return self.get(pr_url).json()

    def post_comment(self, issue_number, body):
        """Create or update comment in pull request comment section."""
        issue_comments_url = urljoin(self.base_url,
                                     "issues/%s/comments" % issue_number)
        issue_comments = self.get(issue_comments_url).json()

        data = {"body": body}

        for issue_comment in issue_comments:
            if issue_comment["user"]["login"] == GH_COMMENTER:
                comment_url = urljoin(
                    self.base_url, "issues/comments/%s" % issue_comment["id"]
                )
                return self.patch(comment_url, data)
        return self.post(issue_comments_url, data)
