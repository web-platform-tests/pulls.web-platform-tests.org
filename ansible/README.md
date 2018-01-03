# Deploying the PR Results Consolidator
The deployment process uses [Ansible](http://docs.ansible.com/) to configure
the server to use [nginx](http://nginx.org/) and
[uWSGI](http://uwsgi-docs.readthedocs.io/en/latest/) to serve a
[Flask](http://flask.pocoo.org/) application. It expects nginx to be able to
use port 80.

This process is based on the [Modern Web Deployment Workflow](https://deployment-workflow.bocoup.com/).

## Requirements

- Ubuntu-like remote server environment
- [git](https://git-scm.com/downloads)
- [Ansible >= 2.3.0.0](http://docs.ansible.com/ansible/intro_installation.html#latest-releases-via-pip)
  - Note: on Ubuntu, this requires installing ansible via `pip`, not `apt`.

# Setting yourself up as a deployer.

The server uses [passwordless SSH](https://help.ubuntu.com/community/SSH/OpenSSH/Keys),
which means you will need a public/private keypair in order to log in.

If you are interested in maintaining the server, you will need to do the
following:

1) Ensure you have [OpenSSL](https://www.openssl.org/) installed on your system and in your path.
2) Generate an encrypted version of the password you would like to use when
   `sudo`-ing on the staging and production servers.
   - `openssl passwd -1 -salt $(openssl rand -base64 6) yourpassword`
3) Add yourself to the list of users in [ansible/group_vars/all/vars.yml](/ansible/group_vars/all/vars.yml). You must include:
  - a) name: Your username for the server. You will use this to SSH into the server instance.
  - b) state: present
  - c) real_name: Your real name
  - d) groups: sudo,www-data
  - e) shadow_pass: The encrypted password you generated in Step 2.
  - f) public_keys: A list of (probably 1) public keys for logging into the
  server. This is more convenient for you if it is your `id_rsa.pub`, but
  you can use a separate keypair if you prefer.
4) Open a PR with these changes.
4) Ask someone already in that file for a copy of their `~/vault_pass` file so
   that you can run the deploy scripts.

## Ansible Vault
This project uses Ansible Vault to encrypt secrets. In order to work, a key
file needs to be shared between the server and the person responsible for
encrypting the secrets file. The process for doing this as the secret
keeper is as follows:

1. Install ansible on your local machine.
2. Create a `~/.vault_pass` (or whatever you want to call it) file in your
   home directory. The contents of this file should only consist of the key
   you would like to use to encrypt and decrypt the secrets file.
   - Recommended: `export ANSIBLE_VAULT_PASSWORD_FILE=~/.vault_pass` to
     to avoid having to refer to that file every time you encrypt/decrypt.
     The rest of the instructions will assume you have done this. If not,
     you will have to add the `--vault-password-file=~/.vault_pass` flag
     to `ansible-vault` commands.
3. Decrypt the existing `wptdash/ansible/group_vars/all/vault` file.
4. Make changes to the following variables as necessary in plain text. Be careful, changes to these values *WILL* break things.
   - `vault_db_password`: The password you would like to use for the
      postgresql user. This can be anything you want.
   - `vault_github_commenter_token`: This must be a GitHub auth token for the
      user that will be commenting on the PRs.
5. Re-encrypt the vault file. Seriously, don't forget to do this. Never commit
   the unencrypted file to the repo.
   - `ansible-vault encrypt vault` from the `wptdash/ansible/group_vars/all
   directory`
6. Commit this file to the repository.

## Deploying Application Changes to a Server

If changes are made to the application code, You must be a user in the users file and the commit you want to deploy must be pushed to GitHub (so Ansible can check
it out). Once done, run `./run-playbook.sh deploy {server} --user=yourusername`
from the root of this repository.

Examples:

1. Deploy `master` to production
  - `./run-playbook.sh deploy production --user=yourusername`
2. Deploy the `test` branch to staging
  - `./run-playbook.sh deploy staging commit=test --user=yourusername`

Useful flags:

- `commit=branch/tag/sha`: The specific branch, tag or SHA (pushed to
  the repo) you would like to deploy. If omitted, defaults to master.
- `--private-key=~/.ssh/key_name`: if you used something other than your
  default `id_rsa.pub` public key when setting up your user.
- `--force=true`: Regardless of the prior deploy state of the commit, reclone
  and rebuild it before symlinking it and making it live.
- `--user=username`: Set the username as which to SSH to the server and run
  the playbook. Must be one of the users configured above.

## Reconfiguring a Server

If changes are made to the configure, db, database, nginx, users, or uwsgi
Ansible roles, you must re-configure the server: `./run-playbook.sh configure {server} --user=yourusername`.

Examples:

1. Reconfigure production
  - `./run-playbook.sh configure production --user=yourusername`
2. Test a configuration on staging
  - `./run-playbook.sh configure staging commit=test-config --user=yourusername`
3. Update the users on the production server without restarting nginx/uWSGI:
  - `.run-playbook.sh configure production --tags=users --user=yourusername`

Useful flags (in addition to those listed above):

- `--tags=role`: Run only a specific Ansible role within the playbook.

## Provisioning a New Server

This is how to install the dependencies and application on a base Ubuntu 16.04
box. If you are maintaining an existing server, this has been done for you.

1. Create a server instance wherever you like.
2. Add a non-root user on the server to own the application.
  - `adduser wptdash` as root
  - You will create a password for this user. Keep it secret. Keep it safe.
3. Ensure the new user is able to `sudo`.
  - `adduser wptdash sudo` as root
4. Ensure you can log into this user with passwordless ssh.
5. Log into the server as the new user.
6. Run the `run-playbook.sh` script with to provision the target (staging or production), using the user you created in step 2.
  - `./run-playbook.sh provision staging --user=wptdash`
  - This will ask for the sudo password for the user. This is the password you created in step 2.
7. Run the `run-playbook.sh` script to configure the target (staging or production), using the user you created in step 2.
  - `./run-playbook.sh configure staging --user=wptdash`
  - This will ask for the sudo password for the user. This is the password you created in step 2.
