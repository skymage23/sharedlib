from . import project_management
__is_initialized=False
__current_project=None

class UninitializedError(Exception):
    def __init__(self):
        super().__init__("Module is uninitialized.")

class FailedInitializationError(Exception):
    def __init__(self, message):
        super().__init__("Failed initialization: {0}".format(message))

class ModuleDoubleInitializationError(Exception):
    def __init__(self):
        super().__init__("Module is already initialized.")

def initialize(project_toml_path=None):
    if __is_initialized:
        raise ModuleDoubleInitializationError()

    if project_toml_path is None:
        project_toml_path = __try_find_project_toml()

    if project_toml_path is None:
        raise 

    #Hello
    __current_project = project_management.Toml.generateProjectFromFile(project_toml_path)

def getCurrentProject():
    if not __is_initialized:
        raise UninitializedError()
