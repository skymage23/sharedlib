import inspect
import pathlib

def getProjectHead():
    return pathlib.Path(inspect.stack()[0][1]).parent


