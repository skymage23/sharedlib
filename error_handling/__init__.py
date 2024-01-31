
def die(mod_name = None, errcode = None):
    if mod_name is None:
        raise ValueError("mod_name cannot be None")
    if errcode is None:
        raise ValueError("errcode cannot be None")
    quit(errcode)

