import json
import os

def config():
    """ Load dev config by default"""
    try:
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        filename = 'dev_config'
        if os.getenv('DEPLOY_ENV') == 'prod':
            print(filename)
            filename = 'prod_config'
        with open(os.path.join(__location__ , f"{filename}.json"), encoding='utf8') as data:
            return json.load(data)
    except FileNotFoundError:
        raise FileNotFoundError("JSON file wasn't found")