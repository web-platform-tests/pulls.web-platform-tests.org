#!/usr/bin/env python
# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import datetime
import json
import pytest
from urllib.parse import urlencode
from pytest_mock import mocker

from jsonschema.exceptions import ValidationError
from wptdash.github import GitHub
import wptdash.models as models
from tests.blueprints.fixtures.payloads import (github_webhook_payload,
                                                travis_webhook_payload,
                                                stability_payload)


class TestRoot(object):

    """Test the application root route."""

    def test_no_pulls(self, client, session):
        """Root route says "No pull requests" when no pulls in DB."""
        session.commit()
        rv = client.get('/')
        assert b'No pull requests' in rv.data

    def test_pulls(self, client, session):
        pull_request = models.PullRequest(state=models.PRStatus.OPEN, number=1,
                                          merged=False, head_sha='abcdef12345',
                                          base_sha='12345abcdef', title='abc',
                                          head_repo_id=1, base_repo_id=1,
                                          head_branch='foo', base_branch='bar',
                                          created_at=datetime.now(),
                                          updated_at=datetime.now())
        session.add(pull_request)
        session.commit()

        rv = client.get('/')
        assert b'Pull Request' in rv.data


class TestPullDetail(object):

    """Test the pull request detail page."""

    def test_no_data(self, client, session):
        """PR detail route says "No information" when no pull in DB."""
        rv = client.get('/pull/1')
        assert b'No information' in rv.data

    def test_no_builds(self, client, session):
        """PR detail route says "No builds" when pull has no build info."""
        owner = models.GitHubUser(login='foo')
        head_repo = models.Repository(name='bar', owner=owner)
        base_repo = models.Repository(name='baz', owner=owner)
        pull_request = models.PullRequest(state=models.PRStatus.OPEN, number=1,
                                          merged=False, head_sha='abcdef12345',
                                          base_sha='12345abcdef', title='abc',
                                          head_repository=head_repo,
                                          base_repository=base_repo,
                                          head_branch='foo', base_branch='bar',
                                          created_at=datetime.now(),
                                          updated_at=datetime.now(), id=1)
        session.add(pull_request)
        session.commit()

        rv = client.get('/pull/1')
        assert b'No builds' in rv.data

    def test_builds(self, client, session):
        """PR detail route displays builds when they exist."""
        owner = models.GitHubUser(login='foo')
        head_repo = models.Repository(name='bar', owner=owner)
        base_repo = models.Repository(name='baz', owner=owner)
        pull_request = models.PullRequest(state=models.PRStatus.OPEN, number=1,
                                          merged=False, head_sha='abcdef12345',
                                          base_sha='12345abcdef', title='abc',
                                          head_repository=head_repo,
                                          base_repository=base_repo,
                                          head_branch='foo', base_branch='bar',
                                          created_at=datetime.now(),
                                          updated_at=datetime.now(), id=1)
        build = models.Build(number=123, status=models.BuildStatus.PENDING,
                             started_at=datetime.now())

        pull_request.builds = [build]

        session.add(pull_request)
        session.commit()

        rv = client.get('/pull/1')
        assert b'Build Number' in rv.data


class TestBuildDetail(object):

    """Test the build request detail page."""

    def test_no_data(self, client, session):
        """PR detail route says "No information" when no pull in DB."""
        rv = client.get('/build/1')
        assert b'No information' in rv.data

    def test_no_jobs(self, client, session):
        """Build detail route says "No jobs" when pull has no job info."""
        owner = models.GitHubUser(login='foo')
        head_repo = models.Repository(name='bar', owner=owner)
        base_repo = models.Repository(name='baz', owner=owner)
        pull_request = models.PullRequest(state=models.PRStatus.OPEN, number=1,
                                          merged=False, head_sha='abcdef12345',
                                          base_sha='12345abcdef', title='abc',
                                          head_repository=head_repo,
                                          base_repository=base_repo,
                                          head_branch='foo', base_branch='bar',
                                          created_at=datetime.now(),
                                          updated_at=datetime.now())
        build = models.Build(number=123, status=models.BuildStatus.PENDING,
                             started_at=datetime.now(), id=1,
                             pull_request=pull_request, jobs=[])
        session.add(build)
        session.commit()

        rv = client.get('/build/123')
        assert b'No jobs' in rv.data

    def test_jobs(self, client, session):
        """Build detail route displays jobs when they exist."""
        owner = models.GitHubUser(login='foo')
        head_repo = models.Repository(name='bar', owner=owner)
        base_repo = models.Repository(name='baz', owner=owner)
        pull_request = models.PullRequest(state=models.PRStatus.OPEN, number=1,
                                          merged=False, head_sha='abcdef12345',
                                          base_sha='12345abcdef', title='abc',
                                          head_repository=head_repo,
                                          base_repository=base_repo,
                                          head_branch='foo', base_branch='bar',
                                          created_at=datetime.now(),
                                          updated_at=datetime.now())
        build = models.Build(number=123, status=models.BuildStatus.PENDING,
                             started_at=datetime.now(), id=1,
                             pull_request=pull_request)

        product = models.Product(name='test:unstable')
        job = models.Job(number=1.1, build=build, product=product,
                         state=models.JobStatus.PASSED, allow_failure=True,
                         started_at=datetime.now(), finished_at=datetime.now())

        build.jobs = [job]

        session.add(build)
        session.commit()

        rv = client.get('/build/123')
        assert b'Job Number' in rv.data


class TestAddPullRequest(object):

    """Test endpoint for adding pull request data from GitHub."""

    def test_no_id(self, client, session, mocker):
        """Payload missing id throws jsonschema ValidationError."""
        mocker.patch('wptdash.blueprints.routes.validate_hmac_signature',
                     return_value=True)
        payload = deepcopy(github_webhook_payload)
        payload['pull_request'].pop('id')
        with pytest.raises(ValidationError):
            client.post('/api/pull', data=json.dumps(payload),
                        content_type='application/json')

    def test_no_number(self, client, session, mocker):
        """Payload missing number throws jsonschema ValidationError."""
        mocker.patch('wptdash.blueprints.routes.validate_hmac_signature',
                     return_value=True)
        payload = deepcopy(github_webhook_payload)
        payload['pull_request'].pop('number')
        with pytest.raises(ValidationError):
            client.post('/api/pull', data=json.dumps(payload),
                        content_type='application/json')

    def test_no_title(self, client, session, mocker):
        """Payload missing title throws jsonschema ValidationError."""
        mocker.patch('wptdash.blueprints.routes.validate_hmac_signature',
                     return_value=True)
        payload = deepcopy(github_webhook_payload)
        payload['pull_request'].pop('title')
        with pytest.raises(ValidationError):
            client.post('/api/pull', data=json.dumps(payload),
                        content_type='application/json')

    def test_no_user(self, client, session, mocker):
        """Payload missing sender throws jsonschema ValidationError."""
        mocker.patch('wptdash.blueprints.routes.validate_hmac_signature',
                     return_value=True)
        payload = deepcopy(github_webhook_payload)
        payload['pull_request'].pop('user')
        with pytest.raises(ValidationError):
            client.post('/api/pull', data=json.dumps(payload),
                        content_type='application/json')

    def test_no_created_at(self, client, session, mocker):
        """Payload missing created_at throws jsonschema ValidationError."""
        mocker.patch('wptdash.blueprints.routes.validate_hmac_signature',
                     return_value=True)
        payload = deepcopy(github_webhook_payload)
        payload['pull_request'].pop('created_at')
        with pytest.raises(ValidationError):
            client.post('/api/pull', data=json.dumps(payload),
                        content_type='application/json')

    def test_no_updated_at(self, client, session, mocker):
        """Payload missing updated_at throws jsonschema ValidationError."""
        mocker.patch('wptdash.blueprints.routes.validate_hmac_signature',
                     return_value=True)
        payload = deepcopy(github_webhook_payload)
        payload['pull_request'].pop('updated_at')
        with pytest.raises(ValidationError):
            client.post('/api/pull', data=json.dumps(payload),
                        content_type='application/json')

    def test_no_merged(self, client, session, mocker):
        """Payload missing merged throws jsonschema ValidationError."""
        mocker.patch('wptdash.blueprints.routes.validate_hmac_signature',
                     return_value=True)
        payload = deepcopy(github_webhook_payload)
        payload['pull_request'].pop('merged')
        with pytest.raises(ValidationError):
            client.post('/api/pull', data=json.dumps(payload),
                        content_type='application/json')

    def test_no_head(self, client, session, mocker):
        """Payload missing head throws jsonschema ValidationError."""
        mocker.patch('wptdash.blueprints.routes.validate_hmac_signature',
                     return_value=True)
        payload = deepcopy(github_webhook_payload)
        payload['pull_request'].pop('head')
        with pytest.raises(ValidationError):
            client.post('/api/pull', data=json.dumps(payload),
                        content_type='application/json')

    def test_no_base(self, client, session, mocker):
        """Payload missing base throws jsonschema ValidationError."""
        mocker.patch('wptdash.blueprints.routes.validate_hmac_signature',
                     return_value=True)
        payload = deepcopy(github_webhook_payload)
        payload['pull_request'].pop('base')
        with pytest.raises(ValidationError):
            client.post('/api/pull', data=json.dumps(payload),
                        content_type='application/json')

    def test_no_state(self, client, session, mocker):
        """Payload missing state throws jsonschema ValidationError."""
        mocker.patch('wptdash.blueprints.routes.validate_hmac_signature',
                     return_value=True)
        payload = deepcopy(github_webhook_payload)
        payload['pull_request'].pop('state')
        with pytest.raises(ValidationError):
            client.post('/api/pull', data=json.dumps(payload),
                        content_type='application/json')

    def test_complete_payload(self, client, session, mocker):
        """Complete webhook payload creates pull request object in db."""
        mocker.patch('wptdash.blueprints.routes.validate_hmac_signature',
                     return_value=True)
        rv = client.post('/api/pull', data=json.dumps(github_webhook_payload),
                         content_type='application/json')
        pr = session.query(models.PullRequest).filter(
            models.PullRequest.id == github_webhook_payload['pull_request']['id']
        ).one_or_none()

        assert pr
        assert pr.number == 1
        assert pr.title == 'Update the README with new information'
        assert pr.state == models.PRStatus.OPEN
        assert pr.creator.id == 6752317
        assert pr.creator.login == 'baxterthehacker'
        assert pr.created_at == datetime.strptime('2015-05-05T23:40:27Z',
                                                  '%Y-%m-%dT%H:%M:%SZ')
        assert not pr.merged
        assert not pr.merger
        assert not pr.merged_at
        assert pr.head_commit.sha == "0d1a26e67d8f5eaf1f6ba5c57fc3c7d91ac0fd1c"
        assert pr.head_commit.user.id == 6752317
        assert pr.head_commit.user.login == 'baxterthehacker'
        assert pr.base_commit.sha == "9049f1265b7d61be4a8904a9a27120d2064dab3b"
        assert pr.base_commit.user.id == 6752317
        assert pr.base_commit.user.login == 'baxterthehacker'
        assert pr.head_repository.id == 35129377
        assert pr.head_repository.name == 'public-repo'
        assert pr.head_repository.owner.id == 6752317
        assert pr.head_repository.owner.login == 'baxterthehacker'
        assert pr.base_repository.id == 35129377
        assert pr.base_repository.name == 'public-repo'
        assert pr.base_repository.owner.id == 6752317
        assert pr.base_repository.owner.login == 'baxterthehacker'
        assert pr.head_branch == 'changes'
        assert pr.base_branch == 'master'
        assert pr.updated_at == datetime.strptime('2015-05-05T23:40:27Z',
                                                  '%Y-%m-%dT%H:%M:%SZ')
        assert not pr.closed_at

    def test_merger_data(self, client, session, mocker):
        """Complete payload PLUS merger data creates merger ref in db."""
        mocker.patch('wptdash.blueprints.routes.validate_hmac_signature',
                     return_value=True)
        payload = deepcopy(github_webhook_payload)
        payload['pull_request']['merged_by'] = {
            'id': 6752317, 'login': 'baxterthehacker'
        }

        rv = client.post('/api/pull', data=json.dumps(payload),
                         content_type='application/json')
        pr = session.query(models.PullRequest).filter(
            models.PullRequest.id == github_webhook_payload['pull_request']['id']
        ).one_or_none()

        assert pr.creator
        assert pr.creator.login == 'baxterthehacker'


class TestAddBuild(object):

    """Test endpoint for adding build data from Travis."""

    def test_no_pr_in_db(self, client, session):
        pass

    def test_no_id(self, client, session):
        """Payload missing id throws jsonschema ValidationError."""
        payload = deepcopy(travis_webhook_payload)
        payload.pop('id')
        with pytest.raises(ValidationError):
            client.post('/api/build', data=dict(payload=json.dumps(payload)))

    def test_no_number(self, client, session):
        """Payload missing number throws jsonschema ValidationError."""
        payload = deepcopy(travis_webhook_payload)
        payload.pop('number')
        with pytest.raises(ValidationError):
            client.post('/api/build', data=dict(payload=json.dumps(payload)))

    def test_no_head_commit(self, client, session):
        """Payload missing head_commit throws jsonschema ValidationError."""
        payload = deepcopy(travis_webhook_payload)
        payload.pop('head_commit')
        with pytest.raises(ValidationError):
            client.post('/api/build', data=dict(payload=json.dumps(payload)))

    def test_no_base_commit(self, client, session):
        """Payload missing base_commit throws jsonschema ValidationError."""
        payload = deepcopy(travis_webhook_payload)
        payload.pop('base_commit')
        with pytest.raises(ValidationError):
            client.post('/api/build', data=dict(payload=json.dumps(payload)))

    def test_no_pull_request(self, client, session):
        """Payload missing pull_request throws jsonschema ValidationError."""
        payload = deepcopy(travis_webhook_payload)
        payload.pop('pull_request')
        with pytest.raises(ValidationError):
            client.post('/api/build', data=dict(payload=json.dumps(payload)))

    def test_no_pull_request_number(self, client, session):
        """Payload missing pull_request_number throws jsonschema ValidationError."""
        payload = deepcopy(travis_webhook_payload)
        payload.pop('pull_request_number')
        with pytest.raises(ValidationError):
            client.post('/api/build', data=dict(payload=json.dumps(payload)))

    def test_no_status(self, client, session):
        """Payload missing status throws jsonschema ValidationError."""
        payload = deepcopy(travis_webhook_payload)
        payload.pop('status')
        with pytest.raises(ValidationError):
            client.post('/api/build', data=dict(payload=json.dumps(payload)))

    def test_no_repository(self, client, session):
        """Payload missing repository throws jsonschema ValidationError."""
        payload = deepcopy(travis_webhook_payload)
        payload.pop('repository')
        with pytest.raises(ValidationError):
            client.post('/api/build', data=dict(payload=json.dumps(payload)))

    # TODO
    # def test_no_product(self, client, session):
    #     """Payload with job missing product adds build but no jobs to DB."""
    #     pass

    # TODO
    # def test_complete_payload(self, client, session, mocker):
    #     """Complete webhook payload creates build object in db."""
    #     mocker.patch('wptdash.travis.Travis.get_verified_payload',
    #                  return_value=travis_webhook_payload)
    #     pull_request = models.PullRequest(state=models.PRStatus.OPEN, number=1,
    #                                       merged=False,
    #                                       head_sha='8d23f9f7c17d28a1454bc4eb5fd40c94eaef4523',
    #                                       base_sha='5f42a82d378f993a1b6401a0d9c6c88c9c227556',
    #                                       title='abc',
    #                                       head_repo_id=1, base_repo_id=1,
    #                                       head_branch='foo', base_branch='bar',
    #                                       created_at=datetime.now(),
    #                                       updated_at=datetime.now())
    #     session.add(pull_request)
    #     session.commit()

    #     rv = client.post('/api/build',
    #                      data=dict(payload=json.dumps(travis_webhook_payload)),
    #                      headers={'SIGNATURE': 'abc'})
    #     build = session.query(models.Build).filter(
    #         models.Build.id == travis_webhook_payload['id']
    #     ).one_or_none()

    #     assert build
    #     assert build.number == travis_webhook_payload['number']
    #     assert build.pull_request.number == 1248
    #     assert build.pull_request.head_sha == travis_webhook_payload['head_commit']
    #     assert build.pull_request.base_sha == travis_webhook_payload['base_commit']
    #     assert build.head_commit.sha == travis_webhook_payload['head_commit']
    #     assert build.base_commit.sha == travis_webhook_payload['base_commit']
    #     assert build.status == models.BuildStatus.PASSED
    #     assert build.started_at == datetime.strptime('2017-06-09T13:55:30Z"',
    #                                                  '%Y-%m-%dT%H:%M:%SZ')
    #     assert build.finished_at == datetime.strptime('2017-06-09T13:58:22Z"',
    #                                                   '%Y-%m-%dT%H:%M:%SZ')
    #     assert len(build.jobs) == 1

    #     job = build.jobs[0]

    #     assert job.number == 2064.1
    #     assert job.product.name == 'chrome:unstable'
    #     assert not job.allow_failure
    #     assert job.started_at == datetime.strptime('2017-06-09T13:55:30Z"',
    #                                                '%Y-%m-%dT%H:%M:%SZ')
    #     assert job.finished_at == datetime.strptime('2017-06-09T13:58:22Z"',
    #                                                 '%Y-%m-%dT%H:%M:%SZ')


class TestUpdateTestMirror(object):

    """Test endpoint for adding pr mirror."""

    def test_no_issue_number(self, client, session):
        """Payload missing issue_number throws jsonschema ValidationError."""
        payload = {'url': 'abc'}
        with pytest.raises(ValidationError):
            client.post('/api/test-mirror', data=json.dumps(payload),
                        content_type='application/json')

    def test_no_url(self, client, session):
        """Payload missing issue_number throws jsonschema ValidationError."""
        payload = {'issue_number': 1}
        with pytest.raises(ValidationError):
            client.post('/api/test-mirror', data=json.dumps(payload),
                        content_type='application/json')

    def test_no_pr(self, client, session):
        """Returns HTTP 422 if no matching PR in database."""
        payload = {'issue_number': 1, 'url': 'abc'}
        rv = client.post('/api/test-mirror', data=json.dumps(payload),
                         content_type='application/json')

        assert rv.status_code == 422

    def test_complete_payload(self, client, session):
        pull_request = models.PullRequest(state=models.PRStatus.OPEN, number=1,
                                          merged=False, head_sha='abcdef12345',
                                          base_sha='12345abcdef', title='abc',
                                          head_repo_id=1, base_repo_id=1,
                                          head_branch='foo', base_branch='bar',
                                          created_at=datetime.now(),
                                          updated_at=datetime.now(), id=1)
        session.add(pull_request)
        session.commit()

        payload = {'issue_number': 1, 'url': 'abc'}
        rv = client.post('/api/test-mirror', data=json.dumps(payload),
                         content_type='application/json')

        mirror = session.query(models.TestMirror).filter(
            models.TestMirror.pull_id == 1
        ).one_or_none()

        assert mirror
        assert mirror.url == 'abc'


class TestAddStabilityCheck(object):

    """Test endpoint for adding stability check."""

    def test_no_pull(self, client, session):
        """Payload missing pull throws jsonschema ValidationError."""
        payload = deepcopy(stability_payload)
        payload.pop('pull')
        with pytest.raises(ValidationError):
            client.post('/api/stability', data=json.dumps(payload),
                        content_type='application/json')

    def test_no_job(self, client, session):
        """Payload missing job throws jsonschema ValidationError."""
        payload = deepcopy(stability_payload)
        payload.pop('job')
        with pytest.raises(ValidationError):
            client.post('/api/stability', data=json.dumps(payload),
                        content_type='application/json')

    def test_no_build(self, client, session):
        """Payload missing build throws jsonschema ValidationError."""
        payload = deepcopy(stability_payload)
        payload.pop('build')
        with pytest.raises(ValidationError):
            client.post('/api/stability', data=json.dumps(payload),
                        content_type='application/json')

    def test_no_product(self, client, session):
        """Payload missing product throws jsonschema ValidationError."""
        payload = deepcopy(stability_payload)
        payload.pop('product')
        with pytest.raises(ValidationError):
            client.post('/api/stability', data=json.dumps(payload),
                        content_type='application/json')

    def test_no_iterations(self, client, session):
        """Payload missing iterations throws jsonschema ValidationError."""
        payload = deepcopy(stability_payload)
        payload.pop('iterations')
        with pytest.raises(ValidationError):
            client.post('/api/stability', data=json.dumps(payload),
                        content_type='application/json')

    def test_no_results(self, client, session):
        """Payload missing results throws jsonschema ValidationError."""
        payload = deepcopy(stability_payload)
        payload.pop('results')
        with pytest.raises(ValidationError):
            client.post('/api/stability', data=json.dumps(payload),
                        content_type='application/json')

    def test_no_pr(self, client, session, mocker):
        """Returns HTTP 422 if no matching PR in database."""
        mocker.spy(GitHub, 'get_pr')
        rv = client.post('/api/stability', data=json.dumps(stability_payload),
                         content_type='application/json')

        assert GitHub.get_pr.call_count == 1

    def test_complete_payload(self, client, session):
        pull_request = models.PullRequest(state=models.PRStatus.OPEN, number=1,
                                          merged=False, head_sha='abcdef12345',
                                          base_sha='12345abcdef', title='abc',
                                          head_repo_id=1, base_repo_id=1,
                                          head_branch='foo', base_branch='bar',
                                          created_at=datetime.now(),
                                          updated_at=datetime.now(), id=1)
        session.add(pull_request)
        session.commit()

        rv = client.post('/api/stability', data=json.dumps(stability_payload),
                         content_type='application/json')

        stability_statuses = session.query(models.StabilityStatus).filter(
            models.StabilityStatus.job_id == 2,
            models.StabilityStatus.test_id == 'curb the dog'
        ).all()

        assert len(stability_statuses) == 2
