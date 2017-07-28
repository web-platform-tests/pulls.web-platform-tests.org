{% set build = pull.builds|sort(attribute='number', reverse=True)|first %}
{% set has_unstable = build.jobs|map(attribute='tests')|map('selectattr', 'consistent', 'sameas', false)|list|length %}

# Build {{ build.status.name }}

Started: {{ build.started_at }}
Finished: {{ build.finished_at }}

> This report has been truncated because the number of unstable tests exceeds GitHub.com's character limit for comments ({{characters}} characters).


{% if has_unstable %}
<h2>Unstable Browsers</h2>
  {% for job in build.jobs|sort(attribute='id') %}
  {% set inconsistent_tests = job.tests|selectattr("consistent", "sameas", false)|list %}
  {% if inconsistent_tests|length %}
  <h3>Browser: "{{ job.product.name|replace(':', ' ')|title }}"<small>{{' (failures allowed)' if job.allow_failure else ''}}</small></h3>
  <p>View in: <a href="http://{{app_domain}}/job/{{job.number}}">Dashboard</a> |
      <a href="https://travis-ci.org/{{org_name}}/{{repo_name}}/jobs/{{job.id}}">TravisCI</a></p>
  {% endif %}
  {% endfor %}
{% else %}

View more information about this build on:

- [WPT Results Dashboard](http://{{app_domain}}/build/{{build.number}})
- [TravisCI](https://travis-ci.org/{{org_name}}/{{repo_name}}/builds/{{build.id}})

{% endif %}
