from fabric.api import task
from fabric.context_managers import lcd
from fabric.operations import local

@task
def build():
    with lcd('./deployment/'):
        local('docker-compose up -d --build')


@task
def test():
    with lcd('./deployment/'):
        local('docker-compose exec authorization pytest')


@task
def backup(target='authorization'):
    exclude = '--exclude auth.permission --exclude contenttypes'
    local("docker exec {} mkdir -p /home/backup".format(target))
    local("docker exec {} sh -c 'python manage.py dumpdata {} > /home/backup/latest.json'".format(target, exclude))


@task
def migrate(target='authorization'):
    local("docker exec {} python manage.py migrate".format(target))

@task
def restore(target):
    pass


@task
def cleanup():
    with lcd('./deployment/'):
        local('docker-compose down')