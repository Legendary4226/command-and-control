def dict_to_dataclass(klass: any, data: dict) -> any:
    try:
        data_object = object.__new__(klass)
        for key, value in data.items():
            setattr(data_object, key, value)
        return data_object
    except:
        return data
