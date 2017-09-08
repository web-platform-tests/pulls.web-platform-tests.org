# Migrating the Database
We use [flask-migrate](http://flask-migrate.readthedocs.io/en/latest/)
to create and deploy database migrations whenever the schema changes.

We use the Flask-Script method of invoking the migration commands. These
commands must be run on a system with an instance of the database installed.
Since you probably don't want to create this on your system, the following
instructions show how to do this on the staging server.

1. Deploy your branch to staging
  - This branch should have the changes to `wptdash/models.py` you want
    to create a migration script for.
  - Commit and push this branch to w3c/wptdash.
    - `./run-playbook.sh deploy staging --user=username commit=branch-name`
2. Log into the staging server
  - `ssh username@pulls-staging.web-platform-tests.org`
3. Escalate to `root` user
  - `sudo bash`
  - We have to do this because we have to write to a directory we do not own
    and  `sudo` does not maintain the virtual environment required to run the
    migration scripts
      - This could be enhanced away by making sure users are in the group that
        owns this directory
4. Enter the virtual environment
  - `cd /var/www/wptdash`
  - `source venv/bin/activate`
5. Create the migration file
  - `cd site`
  - `python manage.py db migrate`
6. Edit the migration file
  - The migration file may not include everything the upgrades and downgrads
    need to do. (See [Alembic docs](http://alembic.zzzcomputing.com/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect)
    for more information)
7. Test the migration file
  - `python manage.py db upgrade`
8. Verify your migration worked by checking the database
  - `su - postgres`
  - `psql -d wptdash`
  - Some useful commands:
    - `SELECT column_name, data_type FROM information_schema.columns WHERE table_name='<tablename>';`
    - `SELECT * FROM <tablename> LIMIT 10;`
9. Copy the migration file to your local system
  - The staging server does not have write access to GitHub
  - SCP or echo and copy the file to your local `migrations/versions` folder.
10. Commit and PR
  - Add the migration file to your PR commits and open a PR
11. Deploy to production
  - After merging to master, deploy to production, SSH in, and run the `python manage.py db upgrade` as you did above.
    - This could be enhanced away by including it in the ansible deploy script.
