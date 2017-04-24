import enum

from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from jsonschema import validate

app = Flask("wptdash")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route("/")
def main():
    return "wpt dashboard"

@app.route("/pull/<int:pull_id>")
def pull_detail(pull_id):
    import models

    pull = db.session.query(models.PullRequest).filter_by(id=pull_id).first()
    return render_template("pull.html", pull=pull)


@app.route("/api/stability", methods=["POST"])
def add_stability_check():
    import models

    schema = {
        "type": "object",
        "properties": {
            "pull_request": {
                "type": "integer"
            },
            "url": {
                "type": "string"
            },
            "product": {
                "type": "string",
                "maxLength": 255,
            },
            "iterations": {
                "type": "integer"
            },
            "status": {
                "type": "string",
                "enum": ["pass", "fail", "error"]
            },
            "message": {
                "type": "string"
            },
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "test": {
                            "type": "string",
                        },
                        "subtest": {
                            "type": ["string", "null"]
                        },
                        "status": {
                            "type": "object",
                            "patternProperties": {
                                "^(?:pass|fail|ok|timeout|error|notrun|crash)$": {
                                    "type": "integer"
                                }
                            }
                        }
                    },
                    "required": ["test", "subtest", "status"]
                }
            }
        },
        "required": ["pull_request", "product", "iterations", "status"]
    }

    data = request.get_json(force=True)
    validate(data, schema)

    pr, _ = models.get_or_create(db.session,
                                 models.PullRequest,
                                 id=data["pull_request"])

    product, _ = models.get_or_create(db.session,
                                      models.StabilityProduct,
                                      name=data["product"])

    job = models.StabilityJob(pull=pr,
                              product=product,
                              status=models.JobStatus.from_string(data["status"]))
    db.session.add(job)

    for result_data in data.get("results", []):
        test, _ = models.get_or_create(db.session,
                                       models.Test,
                                       test=result_data["test"],
                                       subtest=result_data["subtest"])
        result = models.StabilityResult(test=test,
                                        iterations=data["iterations"])
        db.session.add(result)

        for status_name, count in result_data["status"].iteritems():
            status = models.StabilityStatus(result=result,
                                            status=models.TestStatus.from_string(status_name),
                                            count=count)
            db.session.add(status)

    db.session.commit()

    #TODO: make this return some useful JSON
    return "Created job %s" % job.id


if __name__ == "__main__":
    app.run(debug=True)
