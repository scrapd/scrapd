from pathlib import Path

from invoke import task
from nox.virtualenv import VirtualEnv

# Configuration values.
DUMP_DIR = '.dump'
VENV = 'venv'
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
def dump_json(c):
    """Dump errors and create JSON data set."""
    c.run(f'mkdir -p {DUMP_DIR}')
    c.run('scrapd -vvv --dump  1>.dump/dump.json 2>.dump/dump.json.log')


@task
def dump_csv(c):
    """Dump errors and create CSV data set."""
    c.run(f'mkdir -p {DUMP_DIR}')
    c.run('scrapd -vvv --dump --format csv 1>.dump/dump.csv 2>.dump/dump.csv.log')


@task
def flame_graph(c):
    """Create an interactive CPU flame graph."""
    _, venv_bin, _ = get_venv(VENV)
    pyspy = venv_bin / 'py-spy'
    c.run(f'sudo {pyspy.resolve()} -d 20 --flame profile.svg -- {(venv_bin /project_name ).resolve()} -v --pages 5')


@task
def nox(c, s=''):
    """Wrapper for the nox tasks (`inv nox list` for details)."""
    if not s:
        c.run('nox --list')
    else:
        c.run(f'nox -s {s}')


@task
def profile(c):
    """Create an interactive CPU flame graph."""
    _, venv_bin, _ = get_venv(VENV)
    pyinstrument = venv_bin / 'pyinstrument'
    c.run(f'{pyinstrument.resolve()} --renderer html {(venv_bin /project_name ).resolve()} -v --format count --pages 5',
          pty=True)


@task
def publish(c):
    """Publish the documentation."""
    c.run('./.circleci/publish.sh')


@task(default=True)
def setup(c):
    """Setup the developper environment."""
    c.run('nox --envdir .')


def get_venv(venv):
    """
    Return `Path` objects from the venv.

    :param str venv: venv name
    :return: the venv `Path`, the `bin` folder `Path` within the venv, and if specified, the `Path` object of the
        activate script within the venv.
    :rtype: a tuple of 3 `Path` objects.
    """
    location = Path(venv)
    venv = VirtualEnv(location.resolve())
    venv_bin = Path(venv.bin)
    activate = venv_bin / 'activate'
    return venv, venv_bin, activate
