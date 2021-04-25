import json
import os
from types import SimpleNamespace

def config():
    """ Load dev config by default, override with env file """
    try:
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        base_filename = 'base_config'
        filename = 'dev_config'
        if os.getenv('DEPLOY_ENV') == 'prod':
            filename = 'prod_config'
        base_config = open(os.path.join(__location__ , f'{base_filename}.json'), encoding='utf8')
        base_config = json.loads(base_config.read(), object_hook=lambda o: SimpleNamespace(**o))
        env_config = open(os.path.join(__location__ , f'{filename}.json'), encoding='utf8')
        env_config = json.loads(env_config.read(), object_hook=lambda o: SimpleNamespace(**o))
        # Chain env dependent config with base config
        return SimpleNamespace(**base_config.__dict__, **env_config.__dict__)
    except FileNotFoundError:
        raise FileNotFoundError("JSON file wasn't found")