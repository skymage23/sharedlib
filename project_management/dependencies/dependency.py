import .
import pyrsistent

class Dependency(PClass):
    name = pyrsistent.field()
    dependency_type = pyrsistent.field()
    dependency_timing = pyrsistent.field()

    def locate(self, build_environment):
        raise NotImplementedError

    def getParentDirectoryOfInstall(self, build_environment):
        raise NotImplementedError
