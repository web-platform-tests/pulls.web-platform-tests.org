{% set build = pull.builds|sort(attribute='number', reverse=True)|first %}
{% set has_unstable = build.jobs|map(attribute='tests')|map('selectattr', 'consistent', 'sameas', false)|list|length %}

# Build {{ build.status.name }}

Started: {{ build.started_at }}
Finished: {{ build.finished_at }}

{% if has_unstable %}
<h2>Unstable Results</h2>
  {% for job in build.jobs|sort(attribute='id') %}
  {% set inconsistent_tests = job.tests|selectattr("consistent", "sameas", false)|list %}
  {% if inconsistent_tests|length %}
  <h3>Browser: "{{ job.product.name|replace(':', ' ')|title }}"<small>{{' (failures allowed)' if job.allow_failure else ''}}</small></h3>
  <p>View in: <a href="http://{{app_domain}}/job/{{job.number}}">Dashboard</a> |
      <a href="https://travis-ci.org/{{org_name}}/{{repo_name}}/jobs/{{job.id}}">TravisCI</a></p>
  <table>
    <tr>
      <th>Test</th>
      <th>Subtest</th>
      <th>Results</th>
      <th>Messages</th>
    </tr>
  {% for result in inconsistent_tests %}
  {% if not result.test.parent %}
  <tr>
    <td><code>{{ result.test.id }}</code></td>
    <td>&nbsp;</td>
    <td>{% for status in result.statuses %}{{status.status.name}}: {{status.count}}<br />{% endfor %}</td>
    <td>{% if result.messages %}{% set messages = result.messages|fromjson %}{% if messages|length %}{% for message in messages %}<code>{{ message }}</code><br />{% endfor %}{% endif %}{% endif %}</td>
  </tr>
  {% if result.test.subtests|length %}
  {% for subresult in job.tests %}
  {% if subresult.test.parent_id and subresult.test.parent_id == result.test.id and not subresult.test.consistent %}
  <tr>
    <td>&nbsp;</td>
    <td><code>{{ subresult.test.id }}</code></td>
    <td>{% for status in subresult.statuses %}{{status.status.name}}: {{status.count}}<br />{% endfor %}</td>
    <td>{% if subresult.messages %}{% set messages = subresult.messages|fromjson %}{% if messages|length %}{% for message in messages %}<code>{{ message }}</code><br />{% endfor %}{% endif %}{% endif %}</td>
  </tr>
  {% endif %}
  {% endfor %}
  {% endif %}
  {% endif %}
  {% endfor %}
  </table>
  {% endif %}
  {% endfor %}
{% else %}

View more information about this build on:

- [WPT Results Dashboard](http://{{app_domain}}/build/{{build.number}})
- [TravisCI](https://travis-ci.org/{{org_name}}/{{repo_name}}/builds/{{build.id}})

{% endif %}
