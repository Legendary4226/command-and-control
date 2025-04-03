import dataclasses

def dict_to_dataclass(klass: any, d: any):
    try:
        fieldtypes = {f.name:f.type for f in dataclasses.fields(klass)}
        return klass(**{f:dict_to_dataclass(fieldtypes[f], d[f]) for f in d})
    except:
        return d # Not a dataclass field
    