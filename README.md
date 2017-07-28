# PR Results Consolidator

This application listens to pull request webhooks from GitHub, build
notifications from TravisCI, and requests from other bots in the
web-platform-tests ecosystem; consolidates the data from each of those
providers; and posts a single summary comment on the state of the pull request
to the PR in GitHub. The application also provides a UI to allow
web-platform-tests maintainers to browse complete build results.

## Do I need to do something with this?

This application lives on a server, and only web-platform-tests infrastructure
maintainers need concern themselves with it.

## Maintaining the Server

The server is configured an deployed via Ansible. See [that directory](ansible/
) for more details.

## Setting up the bot

The following GitHub and Travis configurations will tie them into the
application and allow the data to be captured.

If you're performing these tasks, you're probably a maintainer of this
project. You should be
[set up as a deployer](ansible#setting-yourself-up-as-a-deployer) (you
will need the `vault_pass` file to make changes here anyway). Read over the
[Ansible Vault](ansible#ansible-vault) section as well.

When changing a secret token in the `vault`, follow this procedure (Remember
to add `--vault-password-file=path-to-vault_pass-file` to these commands if
you haven't exported the `ANSIBLE_VAULT_PASSWORD_FILE=path-to-vault_pass-file`
environment variable on your system):

1. `ansible-vault decrypt ansible/group_vars/all/vault`
2. Change the token value
3. `ansible-vault encrypt ansible/group_vars/all/vault`
4. Commit the change and open a PR.
5. Once approved and merged to master,
   [deploy](ansible#deploying-application-changes-to-a-server) the change.


### Setting up the GitHub Commenter

You need to set up an account on GitHub to act as the user commenting on PRs
with build information, and share the personal access token with this project.

1. Create or log in to the user account that will be commenting on GitHub PRs
   on behalf of this application.
2. Create a personal access token for that user.
  - Go to https://github.com/settings/tokens.
  - Click "Generate new token"
  - On the creation page, name the token and give it at least `public_repo`
    and `user:email` permissions.
3. Set the `vault_github_commenter_token` value in the vault to the personal access token. Commit and deploy.

### Setting up the GitHub Webhook

GitHub needs to send a pull request notification to this application in order
to populate it with PR and commit data. This will require a secret key. See
https://developer.github.com/webhooks/securing/#setting-your-secret-token for
more details.

1. Decide on a secret key that will be shared between the webhook settings and
   the application.
   - `ruby -rsecurerandom -e 'puts SecureRandom.hex(20)'`
2. Add or edit a webhook at https://github.com/s3c/web-platform-tests/settings/hooks/.
  - Payload URL: http://pulls-staging.web-platform-tests.org/api/pull
  - Content type: application/json
  - Secret: the secret key from Step 2
  - Events: Pull Request
  - Active: True
3. Set the `vault_github_webhook_token` value in the vault to the secret key from Step 2. Commit and deploy.

### Setting up the Travis Webhook

Travis needs to send a build notification to this application in order to
populate it with build status data.

1. Change `notifications.webhooks` in `.travis.yml` (probably at the bottom) in
   https://github.com/w3c/web-platform-tests to point to
   `http://pulls.web-platform-tests.org/api/build`.

## Security Model

### GitHub

The GitHub webhook payload includes a secret token to verify that the request
is issued from the correct repository.

Requests to this endpoint without the correct token will return `401 Unauthorized`.

See https://developer.github.com/webhooks/securing/#setting-your-secret-token
for more information.

### Travis

The Travis webhook payload includes a secret token to verify that the request
originates from Travis. This does not ensure that the request is spawned by a
build in w3c/web-platform-tests, so we perform an extra validation step to
make sure the Travis payload has an organization name and repository name
that match the expected values.

Requests to this endpoint without the correct Travis signature header will return `401 Unauthorized`.

Requests to this endpoint that do not match the organization name and repository name will return `403 Forbidden`.
