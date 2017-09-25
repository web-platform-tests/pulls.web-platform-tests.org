#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import datetime, timedelta
from sqlalchemy import or_
from statistics import mean, median

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


def get_jobs_for_metrics(db, models, start_date, end_date):
    first_complete_jobs = []

    jobs = db.session.query(models.Job).filter(
        models.Job.product_id == models.Product.id
    ).filter(
        models.Job.build_id == models.Build.id
    ).filter(
        models.Build.pull_request_id == models.PullRequest.id
    ).filter(
        or_(models.Product.name.ilike('%firefox%'),
            models.Product.name.ilike('%chrome%'),
            models.Product.name.ilike('%safari%'),
            models.Product.name.ilike('%microsoft%'))
    ).filter(models.PullRequest.created_at >= datetime.strptime(
        '%sT00:00:00Z' % start_date, DATETIME_FORMAT
    ), models.PullRequest.created_at < datetime.strptime(
        '%sT00:00:00Z' % end_date, DATETIME_FORMAT
    )).order_by(
        models.PullRequest.created_at.asc(),
        models.Build.started_at.asc(),
        models.Job.started_at.asc(),
        models.Job.product_id.asc()
    ).all()

    seen_jobs = {}
    for job in jobs:
        job_identifier = '%s-%s' % (job.build.pull_request.id, job.product_id)
        if job_identifier not in seen_jobs or seen_jobs[job_identifier] not in ['PASSED', 'FAILED', 'FINISHED']:
            first_complete_jobs.append(job)
            seen_jobs[job_identifier] = job.state.name

    return first_complete_jobs


def get_jobs_by_delta(jobs):
    deltas = [5, 15, 30, 60, 120, 240, 1440]
    jobs_by_delta = defaultdict(int)

    for job in jobs:
        job_finished_at = job.finished_at or job.build.finished_at or datetime.utcnow()
        job_delta = job_finished_at - job.build.pull_request.created_at
        for delta in deltas:
            if job_delta <= timedelta(minutes=delta) and job.state.name in [
                'PASSED', 'FAILED', 'FINISHED'
            ]:
                jobs_by_delta[delta] += 1.0

    for key, completed in jobs_by_delta.items():
        jobs_by_delta[key] = completed * 100 / len(jobs)

    return jobs_by_delta


def get_cumulative_chart_data(jobs):
    total_times = defaultdict(int)
    cumulative_chart_data = []

    for job in jobs:
        job_finished_at = job.finished_at or job.build.finished_at or datetime.utcnow()
        job_delta = job_finished_at - job.build.pull_request.created_at
        job_delta_minutes = round(job_delta.total_seconds() / 60)
        total_times[job_delta_minutes] += 1

    for minutes, job_totals in total_times.items():
        cumulative_chart_data.append({
            'minutes': minutes,
            'jobs': job_totals
        })
    cumulative_chart_data = sorted(cumulative_chart_data,
                                   key=lambda d: d['minutes'])
    cumulative_sum = 0
    for point in cumulative_chart_data:
        cumulative_sum += point['jobs']
        point['sum'] = cumulative_sum

    return cumulative_chart_data


def get_histogram_data(jobs):
    wait_times = []
    build_times = []

    for job in jobs:
        job_finished_at = job.finished_at or job.build.finished_at or datetime.utcnow()
        build_started_at = job.build.started_at or job.build.pull_request.created_at
        total_time = job_finished_at - job.build.pull_request.created_at
        wait_time = build_started_at - job.build.pull_request.created_at
        build_time = total_time - wait_time
        wait_times.append(wait_time.total_seconds() / 60)
        build_times.append(build_time.total_seconds() / 60)

    return wait_times, build_times


def get_outlier_prs(jobs):
    prs = defaultdict(lambda: {'number': None, 'title': None,
                               'time': timedelta(minutes=0)})

    for job in jobs:
        job_finished_at = job.finished_at or job.build.finished_at or datetime.utcnow()
        total_time = job_finished_at - job.build.pull_request.created_at
        if total_time > timedelta(minutes=60):
            pr_number = job.build.pull_request.number
            prs[pr_number] = {
                'number': pr_number,
                'title': job.build.pull_request.title,
                'time': max(total_time, prs[pr_number]['time'])
            }
    return sorted(prs.values(), key=lambda pr: pr['time'], reverse=True)


def get_statistics(wait_times, build_times):
    return {
        'wait_min': min(wait_times),
        'wait_median': median(wait_times),
        'wait_mean': mean(wait_times),
        'wait_max': max(wait_times),
        'build_min': min(build_times),
        'build_median': median(build_times),
        'build_mean': mean(build_times),
        'build_max': max(build_times),
    }
