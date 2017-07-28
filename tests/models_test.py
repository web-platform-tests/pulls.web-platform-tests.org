#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import pytest
import sqlalchemy
import wptdash.models as models


class TestBuild(object):

    """Test the Build model class."""

    def test_build_no_number(self, session):
        """A build without build number should throw Integrity Error."""
        build = models.Build(status=models.BuildStatus.PENDING)

        session.add(build)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_build_no_status(self, session):
        """A build without status should throw Integrity Error."""
        build = models.Build(number=123)

        session.add(build)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_build_complete(self, session):
        """A build with all required fields should be added to DB."""
        build = models.Build(number=123, status=models.BuildStatus.PENDING)

        session.add(build)
        session.commit()

        builds = session.query(models.Build).all()
        assert build in builds


class TestCommit(object):

    """Test the Commit model class."""

    def test_commit_no_sha(self, session):
        """A commit without sha should throw Integrity Error."""
        commit = models.Commit(user_id=1)

        session.add(commit)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_commit_complete(self, session):
        """A commit with all required fields should be added to DB."""
        commit = models.Commit(sha='abcde12345', user_id=1)

        session.add(commit)
        session.commit()

        commits = session.query(models.Commit).all()
        assert commit in commits


class TestGitHubUser(object):

    """Test the Commit model class."""

    def test_github_user_no_name(self, session):
        """A github_user without name should throw Integrity Error."""
        github_user = models.GitHubUser()

        session.add(github_user)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_github_user_complete(self, session):
        """A github_user with all required fields should be added to DB."""
        github_user = models.GitHubUser(login='foo')

        session.add(github_user)
        session.commit()

        github_users = session.query(models.GitHubUser).all()
        assert github_user in github_users


class TestJob(object):

    """Test the Job model class."""

    def test_job_no_build_id(self, session):
        """A job without build_id should throw Integrity Error."""
        job = models.Job(product_id=1, state=models.JobStatus.PASSED,
                         allow_failure=False)

        session.add(job)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_job_no_product_id(self, session):
        """A job without product_id should throw Integrity Error."""
        job = models.Job(build_id=1, state=models.JobStatus.PASSED,
                         allow_failure=False)

        session.add(job)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_job_no_allow_failure(self, session):
        """A job withoutn allow_failure should throw Integrity Error."""
        job = models.Job(build_id=1, product_id=1,
                         state=models.JobStatus.PASSED)

        session.add(job)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_job_complete(self, session):
        """A job with all required fields should be added to DB."""
        job = models.Job(build_id=1, product_id=1,
                         state=models.JobStatus.PASSED, allow_failure=False)

        session.add(job)
        session.commit()

        jobs = session.query(models.Job).all()
        assert job in jobs


class TestJobResult(object):

    """Test the JobResult model class."""

    def test_job_result_no_job_id(self, session):
        """A job_result without job_id should throw Integrity Error."""
        job_result = models.JobResult(test_id='foo', iterations=10)

        session.add(job_result)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_job_result_no_test_id(self, session):
        """A job_result without test_id should throw Integrity Error."""
        job_result = models.JobResult(job_id=1, iterations=10)

        session.add(job_result)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_job_result_no_iterations(self, session):
        """A job_result without iterations should throw Integrity Error."""
        job_result = models.JobResult(job_id=1, test_id='foo')

        session.add(job_result)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_job_result_no_consistent(self, session):
        """A job_result without iterations should throw Integrity Error."""
        job_result = models.JobResult(job_id=1, test_id='foo', iterations=10)

        session.add(job_result)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_job_result_complete(self, session):
        """A job_result with all required fields should be added to DB."""
        job_result = models.JobResult(job_id=1, test_id='foo', iterations=10,
                                      consistent=False)

        session.add(job_result)
        session.commit()

        job_result_db = models.JobResult.query.one()
        job_result_tuple = (job_result.job_id, job_result.test_id,
                            job_result.iterations)
        job_result_db_tuple = (job_result_db.job_id, job_result_db.test_id,
                               job_result_db.iterations)
        assert job_result_tuple == job_result_db_tuple

    def test_job_result_duplicate(self, session):
        """job_result with duplicate job_id & test_id should not be allowed."""
        job_result = models.JobResult(job_id=1, test_id='foo', iterations=10,
                                      consistent=False)
        job_result_2 = models.JobResult(job_id=1, test_id='foo', iterations=1,
                                        consistent=True)

        session.add(job_result)
        session.add(job_result_2)

        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_job_result_some_duplicate(self, session):
        """job_result with same job_id, but different test_id is allowed."""
        job_result_1 = models.JobResult(job_id=1, test_id='foo', iterations=10,
                                        consistent=False)
        job_result_2 = models.JobResult(job_id=1, test_id='foo2', iterations=1,
                                        consistent=True)

        session.add(job_result_1)
        session.add(job_result_2)

        job_result_1_db = models.JobResult.query.filter(models.JobResult.test_id == 'foo').one()
        job_result_2_db = models.JobResult.query.filter(models.JobResult.test_id == 'foo2').one()
        job_result_1_tuple = (job_result_1.job_id, job_result_1.test_id,
                              job_result_1.iterations)
        job_result_1_db_tuple = (job_result_1_db.job_id, job_result_1_db.test_id,
                                 job_result_1_db.iterations)
        job_result_2_tuple = (job_result_2.job_id, job_result_2.test_id,
                              job_result_2.iterations)
        job_result_2_db_tuple = (job_result_2_db.job_id, job_result_2_db.test_id,
                                 job_result_2_db.iterations)
        assert job_result_1_tuple == job_result_1_db_tuple and job_result_2_tuple == job_result_2_db_tuple


class TestProduct(object):

    """Test the Product model class."""

    def test_product_no_name(self, session):
        """A product without name should throw Integrity Error."""
        product = models.Product()

        session.add(product)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_product_complete(self, session):
        """A product with all required fields should be added to DB."""
        product = models.Product(name='foo')

        session.add(product)
        session.commit()

        products = session.query(models.Product).all()
        assert product in products


class TestPullRequest(object):

    """Test the PullRequest model class."""

    def test_pull_request_no_title(self, session):
        """A pull_request with all required fields should be added to DB."""
        pull_request = models.PullRequest(state=models.PRStatus.OPEN, number=1,
                                          merged=False, head_sha='abcdef12345',
                                          base_sha='12345abcdef',
                                          head_repo_id=1, base_repo_id=1,
                                          head_branch='foo', base_branch='bar',
                                          created_at=datetime.now(),
                                          updated_at=datetime.now())

        session.add(pull_request)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_pull_request_no_state(self, session):
        """A pull_request without state should throw Integrity Error."""
        pull_request = models.PullRequest(number=1,
                                          merged=False, head_sha='abcdef12345',
                                          base_sha='12345abcdef', title='abc',
                                          head_repo_id=1, base_repo_id=1,
                                          head_branch='foo', base_branch='bar',
                                          created_at=datetime.now(),
                                          updated_at=datetime.now())

        session.add(pull_request)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_pull_request_no_number(self, session):
        """A pull_request without number should throw Integrity Error."""
        pull_request = models.PullRequest(state=models.PRStatus.OPEN,
                                          merged=False, head_sha='abcdef12345',
                                          base_sha='12345abcdef', title='abc',
                                          head_repo_id=1, base_repo_id=1,
                                          head_branch='foo', base_branch='bar',
                                          created_at=datetime.now(),
                                          updated_at=datetime.now())

        session.add(pull_request)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_pull_request_no_merged(self, session):
        """A pull_request without merged should throw Integrity Error."""
        pull_request = models.PullRequest(state=models.PRStatus.OPEN, number=1,
                                          head_sha='abcdef12345',
                                          base_sha='12345abcdef', title='abc',
                                          head_repo_id=1, base_repo_id=1,
                                          head_branch='foo', base_branch='bar',
                                          created_at=datetime.now(),
                                          updated_at=datetime.now())

        session.add(pull_request)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_pull_request_no_head_sha(self, session):
        """A pull_request without head_sha should throw Integrity Error."""
        pull_request = models.PullRequest(state=models.PRStatus.OPEN, number=1,
                                          merged=False,
                                          base_sha='12345abcdef', title='abc',
                                          head_repo_id=1, base_repo_id=1,
                                          head_branch='foo', base_branch='bar',
                                          created_at=datetime.now(),
                                          updated_at=datetime.now())

        session.add(pull_request)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_pull_request_no_base_sha(self, session):
        """A pull_request without base_sha should throw Integrity Error."""
        pull_request = models.PullRequest(state=models.PRStatus.OPEN, number=1,
                                          title='abc',
                                          merged=False, head_sha='abcdef12345',
                                          head_repo_id=1, base_repo_id=1,
                                          head_branch='foo', base_branch='bar',
                                          created_at=datetime.now(),
                                          updated_at=datetime.now())

        session.add(pull_request)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_pull_request_no_head_repo_id(self, session):
        """A pull_request without head_repo_id should throw Integrity Error."""
        pull_request = models.PullRequest(state=models.PRStatus.OPEN, number=1,
                                          merged=False, head_sha='abcdef12345',
                                          base_sha='12345abcdef', title='abc',
                                          base_repo_id=1,
                                          head_branch='foo', base_branch='bar',
                                          created_at=datetime.now(),
                                          updated_at=datetime.now())

        session.add(pull_request)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_pull_request_no_base_repo_id(self, session):
        """A pull_request without base_repo_id should throw Integrity Error."""
        pull_request = models.PullRequest(state=models.PRStatus.OPEN, number=1,
                                          merged=False, head_sha='abcdef12345',
                                          base_sha='12345abcdef', title='abc',
                                          head_repo_id=1,
                                          head_branch='foo', base_branch='bar',
                                          created_at=datetime.now(),
                                          updated_at=datetime.now())

        session.add(pull_request)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_pull_request_no_head_branch(self, session):
        """A pull_request without head_branch should throw Integrity Error."""
        pull_request = models.PullRequest(state=models.PRStatus.OPEN, number=1,
                                          merged=False, head_sha='abcdef12345',
                                          base_sha='12345abcdef', title='abc',
                                          head_repo_id=1, base_repo_id=1,
                                          base_branch='bar',
                                          created_at=datetime.now(),
                                          updated_at=datetime.now())

        session.add(pull_request)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_pull_request_no_base_branch(self, session):
        """A pull_request without base_repo_id should throw Integrity Error."""
        pull_request = models.PullRequest(state=models.PRStatus.OPEN, number=1,
                                          merged=False, head_sha='abcdef12345',
                                          base_sha='12345abcdef', title='abc',
                                          head_repo_id=1, base_repo_id=1,
                                          head_branch='foo',
                                          created_at=datetime.now(),
                                          updated_at=datetime.now())

        session.add(pull_request)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_pull_request_no_created_at(self, session):
        """A pull_request without created_at should throw Integrity Error."""
        pull_request = models.PullRequest(state=models.PRStatus.OPEN, number=1,
                                          merged=False, head_sha='abcdef12345',
                                          base_sha='12345abcdef', title='abc',
                                          head_repo_id=1, base_repo_id=1,
                                          head_branch='foo', base_branch='bar',
                                          updated_at=datetime.now())

        session.add(pull_request)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_pull_request_no_updated_at(self, session):
        """A pull_request without updated_at should throw Integrity Error."""
        pull_request = models.PullRequest(state=models.PRStatus.OPEN, number=1,
                                          merged=False, head_sha='abcdef12345',
                                          base_sha='12345abcdef', title='abc',
                                          head_repo_id=1, base_repo_id=1,
                                          head_branch='foo', base_branch='bar',
                                          created_at=datetime.now())

        session.add(pull_request)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_pull_request_complete(self, session):
        """A pull_request with all required fields should be added to DB."""
        pull_request = models.PullRequest(state=models.PRStatus.OPEN, number=1,
                                          merged=False, head_sha='abcdef12345',
                                          base_sha='12345abcdef', title='abc',
                                          head_repo_id=1, base_repo_id=1,
                                          head_branch='foo', base_branch='bar',
                                          created_at=datetime.now(),
                                          updated_at=datetime.now())

        session.add(pull_request)
        session.commit()

        pull_requests = session.query(models.PullRequest).all()
        assert pull_request in pull_requests


class TestRepository(object):

    """Test the Repository model class."""

    def test_repository_no_name(self, session):
        """A repository without name should throw Integrity Error."""
        repository = models.Repository(owner_id=1)

        session.add(repository)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_repository_no_owner_id(self, session):
        """A repository without owner_id should throw Integrity Error."""
        repository = models.Repository(name='foo')

        session.add(repository)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_repository_complete(self, session):
        """A repository with all required fields should be added to DB."""
        repository = models.Repository(name='foo', owner_id=1)

        session.add(repository)
        session.commit()

        repositories = session.query(models.Repository).all()
        assert repository in repositories


class TestStabilityStatus(object):

    """Test the StabilityStatus model class."""

    def test_stability_status_no_job_id(self, session):
        """A stability_status without job_id should throw Integrity Error."""
        stability_status = models.StabilityStatus(
            test_id=1, status=models.TestStatus.PASS, count=10
        )

        session.add(stability_status)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_stability_status_no_test_id(self, session):
        """A stability_status without test_id should throw Integrity Error."""
        stability_status = models.StabilityStatus(
            job_id=1, status=models.TestStatus.PASS, count=10
        )

        session.add(stability_status)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_stability_status_no_status(self, session):
        """A stability_status without status should throw Integrity Error."""
        stability_status = models.StabilityStatus(
            job_id=1, test_id=1, count=10
        )

        session.add(stability_status)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_stability_status_no_count(self, session):
        """A stability_status without count should throw Integrity Error."""
        stability_status = models.StabilityStatus(
            job_id=1, test_id=1, status=models.TestStatus.PASS
        )

        session.add(stability_status)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_stability_status_complete(self, session):
        """A stability_status with all required fields should be added to DB."""
        stability_status = models.StabilityStatus(
            job_id=1, test_id=1, status=models.TestStatus.PASS, count=10
        )

        session.add(stability_status)
        session.commit()

        statuses = session.query(models.StabilityStatus).all()
        assert stability_status in statuses


class TestTest(object):

    """Test the Test model class."""

    def test_stability_status_no_count(self, session):
        """A test without id should throw Integrity Error."""
        test = models.Test()

        session.add(test)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            session.commit()

    def test_repository_complete(self, session):
        """A test with all required fields should be added to DB."""
        test = models.Test(id='foo')

        session.add(test)
        session.commit()

        tests = session.query(models.Test).all()
        assert test in tests


class TestTestMirror(object):

    """Test the TestMirror model class."""

    def test_test_mirror_no_pull_id(self, session):
        """A test without pull_id should throw Integrity Error."""
        test = models.TestMirror(url=None)

        session.add(test)
        with pytest.raises(sqlalchemy.orm.exc.FlushError):
            session.commit()


class TestGetOrCreate(object):

    """Test the get_or_create function."""

    def test_get(self, session):
        """It should retrieve an existing object from the database."""
        test = models.Test(id='foo')

        session.add(test)
        session.commit()

        instance, _ = models.get_or_create(session, models.Test, id='foo')

        assert instance and not _

    def test_create(self, session):
        """It should create and return a new object."""
        instance, _ = models.get_or_create(session, models.Test, id='bar')

        assert instance and _
