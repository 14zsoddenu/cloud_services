import contextlib
from functools import wraps
from time import sleep

import docker
import redis
from docker.errors import NotFound
from dockerctx import new_container
from loguru import logger
from redis import BusyLoadingError

from config import DEV_REDIS
from constants import REDIS_CONTAINER_CONFIG
from rediska import redis_db


def get_container_host_ports(container):
    result = {}
    for internal_port_string, host_ips_dicts_list in container.ports.items():
        inner_port = int(internal_port_string.split("/")[0])
        if host_ips_dicts_list is not None:
            for host_ips_dict in host_ips_dicts_list:
                host_is_valid = "HostIp" in host_ips_dict and "0.0.0.0" in host_ips_dict["HostIp"]
                if host_is_valid:
                    if "HostPort" in host_ips_dict:
                        outer_port = int(host_ips_dict["HostPort"])
                        result[outer_port] = inner_port
    return result


def close_containers_with_ports(outer_ports):
    client = docker.DockerClient()
    containers = client.containers.list(all=True)
    for container in containers:
        ports_map = get_container_host_ports(container)
        if set(outer_ports) == set(ports_map.keys()):
            logger.debug(f"Stopping container {container.short_id}")
            container.stop()


@contextlib.contextmanager
def run_container_from_config(container_config, wait_func=None):
    if "ports" in container_config:
        outer_ports = container_config["ports"].values()
        close_containers_with_ports(outer_ports)

    with contextlib.suppress(NotFound):
        with new_container(**container_config) as c:
            logger.debug(f"Waiting for {container_config['image_name']}")
            if wait_func:
                wait_func()
            yield c
            logger.debug(f"Stopping {container_config['image_name']}")


def wait_for_redis_startup():
    loaded = False
    while not loaded:
        try:
            loaded = "abrakadabra" in redis_db
            if not loaded:
                loaded = True
        except (BusyLoadingError, redis.exceptions.ConnectionError) as e:
            logger.debug("Waiting for Redis to load...")
            sleep(1)


def with_dev_redis(func):
    @wraps(func)
    def dev_redis_context(*args, **kwargs):
        with run_container_from_config(REDIS_CONTAINER_CONFIG, wait_for_redis_startup):
            return func(*args, **kwargs)

    return dev_redis_context if DEV_REDIS else func
