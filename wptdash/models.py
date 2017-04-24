import enum
import sys

from app import db

class PRStatus(enum.Enum):
    open = 1
    closed = 2


class TestStatus(enum.Enum):
    PASS = 1
    FAIL = 2
    OK = 3
    TIMEOUT = 4
    ERROR = 5
    NOTRUN = 6
    CRASH = 7

    @classmethod
    def from_string(cls, status):
        return getattr(cls, status.upper())

class JobStatus(enum.Enum):
    PASS = 1
    FAIL = 2
    ERROR = 3

    @classmethod
    def from_string(cls, status):
        return getattr(cls, status.upper())


user_pr_table = db.Table('user_pr', db.metadata,
                         db.Column('pull_id', db.Integer, db.ForeignKey('pull_request.id')),
                         db.Column('user_id', db.Integer, db.ForeignKey('github_user.id')))


class PullRequest(db.Model):
    __tablename__ = "pull_request"

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Enum(PRStatus))
    mirror = db.relationship("W3CTestMirror",
                             uselist=False)
    stability_jobs = db.relationship("StabilityJob",
                                     back_populates="pull")
    notifications = db.relationship("GitHubUser",
                                    secondary=user_pr_table,
                                    back_populates="pulls")


class W3CTestMirror(db.Model):
    __tablename__ = "w3c_test_mirror"

    pull_id = db.Column(db.Integer,
                        db.ForeignKey("pull_request.id"),
                        primary_key=True)
    pull = db.relationship(PullRequest,
                           back_populates="mirror",
                           uselist=False)
    url = db.Column(db.String, nullable=True)


class StabilityJob(db.Model):
    __tablename__ = "stability_job"

    id = db.Column(db.Integer, primary_key=True)
    pull_id = db.Column(db.Integer,
                        db.ForeignKey("pull_request.id"))
    pull = db.relationship(PullRequest,
                           back_populates='stability_jobs')
    log_url = db.Column(db.String, nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey("stability_product.id"))
    product = db.relationship("StabilityProduct",
                              back_populates="jobs",
                              uselist=False)
    status = db.Column(db.Enum(JobStatus))
    error = db.relationship("StabilityError",
                            back_populates='job',
                            uselist=False)


class StabilityError(db.Model):
    __tablename__ = "stability_error"

    job_id = db.Column(db.Integer,
                       db.ForeignKey("stability_job.id"),
                       primary_key=True)
    job = db.relationship("StabilityJob",
                          back_populates='error')
    message = db.Column(db.Text)


class StabilityProduct(db.Model):
    __tablename__ = "stability_product"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    jobs = db.relationship("StabilityJob",
                           back_populates="product")

class Test(db.Model):
    __tablename__ = "test"

    id = db.Column(db.Integer, primary_key=True)
    test = db.Column(db.Text, nullable=False)
    subtest = db.Column(db.Text, nullable=True)
    results = db.relationship("StabilityResult",
                              back_populates="test")


class StabilityResult(db.Model):
    __tablename__ = "stability_result"

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey("test.id"))
    test = db.relationship(Test,
                           back_populates="results")
    iterations = db.Column(db.Integer)
    statuses = db.relationship("StabilityStatus",
                               back_populates="result")


class StabilityStatus(db.Model):
    __tablename__ = "stability_status"

    result_id = db.Column(db.Integer,
                          db.ForeignKey("stability_result.id"),
                          primary_key=True)
    result = db.relationship("StabilityResult",
                             back_populates="statuses")
    status = db.Column(db.Enum(TestStatus))
    count = db.Column(db.Integer)


class GitHubUser(db.Model):
    __tablename__ = "github_user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    pulls = db.relationship("PullRequest",
                            secondary=user_pr_table,
                            back_populates="notifications")


def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.iteritems())
        params.update(defaults or {})
        instance = model(**params)
        session.add(instance)
        return instance, True

