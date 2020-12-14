import uuid
import yaml

cache = None


def read_cache(file):
    global cache

    with open(file) as f:
        _ = yaml.load(f, Loader=yaml.FullLoader)
        if _:
            cache = _


def get_uuid(key_parts):
    global cache

    key_parts = [str(k) for k in key_parts]

    if not cache:
        cache = dict()

    value = cache
    for i in range(len(key_parts)):
        k = key_parts[i]
        if k not in value:
            if i == len(key_parts) - 1:
                value[k] = str(uuid.uuid4())
                return value[k]
            else:
                value[k] = dict()
        else:
            if i == len(key_parts) - 1:
                return value[k]

        value = value[k]


def write_cache(file):
    with open(file, 'w') as f:
        yaml.dump(cache, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
