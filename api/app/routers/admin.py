from fastapi import APIRouter
from typing import Optional
from . import mongo
import docker

client = docker.from_env()

router = APIRouter()
db = mongo.secure_code_platform

@router.get('/containers_list')
def container_list():
    return [container.name for container in client.containers.list()]

@router.get('/check_database')
def check_database():
    return mongo.list_database_names()

@router.post('/run_example_container')
def run_containers(names: Optional[list] = None):
    client.containers.run(image='example_server',
                          name='example_server',
                          auto_remove=True,
                          detach=True,
                          network='checkers-network',
                          command=['python3', '/app/server.py']
                          )
    server = client.containers.get('example_server')
    return {'ip': server.attrs['NetworkSettings']['Networks']['checkers-network']['IPAddress']}


@router.post('/run_web_checkers_containers')
def run_web_checkers_containers():
    container_ip = run_web_container_with_flag('example_server',
                                               'checkers-network',
                                               'Flag{checker_example_flag}')
    return {'container_ip': container_ip}


@router.post('/run_web_containers')
def run_containers():
    container_ip = run_web_container_with_flag('example_server',
                                               None,
                                               'Flag{checker_example_flag}',
                                               ports={'5000/tcp': 5000},
                                               prod=True)

    return {'container_ip': container_ip}


def get_container_ip(container_name, prod):
    container = client.containers.get(container_name)
    if prod:
        return container.attrs['NetworkSettings']['IPAddress']
    else:
        return container.attrs['NetworkSettings']['Networks']['checkers-network']['IPAddress']


def run_web_container_with_flag(docker_image_name, network, flag, ports=None, prod=False):
    if prod:
        container_name = docker_image_name.split('/')[-1]
    else:
        container_name = 'checker_' + docker_image_name.split('/')[-1]
    client.containers.run(image=docker_image_name,
                          name=container_name,
                          auto_remove=True,
                          detach=True,
                          network=network,
                          ports=ports,
                          environment=[f'SCP_FLAG={flag}'],
                          command=['python3', '/app/server.py']
                          )
    return get_container_ip(container_name, prod)
