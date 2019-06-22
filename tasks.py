from invoke import task

# Configuration values.
project_name = 'scrapd'
docker_org = 'scrapd'
docker_repo = f'{docker_org}/{project_name}'


@task
def build_docker(c):
    """Build a docker image."""
    tag = c.run('git describe', hide=True)
    docker_img = f'{docker_repo}:{tag.stdout.strip()}'
    c.run(f'docker build -t {docker_img} .')


@task
def clean(c):
    """Remove unwanted files and artifacts in this project (!DESTRUCTIVE!)."""
    clean_docker(c)
    clean_repo(c)


@task
def clean_docker(c):
    """Remove all docker images built for this project (!DESTRUCTIVE!)."""
    c.run(f'docker image rm -f $(docker image ls --filter reference={docker_repo} -q) || true')


@task
def clean_repo(c):
    """Remove unwanted files in project (!DESTRUCTIVE!)."""
    c.run('git clean -ffdx')
    c.run('git reset --hard')


@task
def nox(c, s=''):
    """Wrapper for the nox tasks (`inv nox list` for details)."""
    if not s:
        c.run('nox --list')
    else:
        c.run(f'nox -s {s}')


@task
def publish(c):
    """Publish the documentation."""
    c.run('./.circleci/publish.sh')


@task(default=True)
def setup(c):
    """Setup the developper environment."""
    c.run('nox --envdir .')
