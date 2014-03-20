import requests
from hydraclient.core import client as core_client


session = requests.Session()


def get(*args, **kwargs):
    return core_client.get(session, *args, **kwargs)
