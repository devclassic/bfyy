from models import Dict


async def get_dict(key):
    dict = await Dict.get_or_none(key=key)
    if not dict:
        return None
    return dict.value


async def set_dict(key, value):
    dict = await Dict.get_or_none(key=key)
    if not dict:
        dict = Dict(key=key, value=value)
    else:
        dict.value = value
    await dict.save()
