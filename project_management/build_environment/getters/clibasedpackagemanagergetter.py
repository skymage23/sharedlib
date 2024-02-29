import .project_management.build_environment.getters

#When you are processing CLI output, it can be a mess and
#app-specific. Thus, we TRY to force workflows just to keep
#this subsystem of the library on topic, but there are points
#where we require that code be provided by subclasses
#to make sense of CLI program output.  We implement
#these requirements as required callbacks for
#a small number of scenarios this library needs to handle.

class CliBasedPackageManagerGetter(PackageManagerGetter):

    def __init__(self):
        raise NotImplementedError

    def getRepoAddCommand(self):
        raise NotImplementedError:

    def onRepoAddFailure(self):
        raise NotImplementedError

    def onRepoAddSuccess(self):
        raise NotImplementedError

    #This sequence gets executed sequentially, so, MAKE SURE THE ORDER IS CORRECT!
    def getRepoAddCommandSequence(self)  #Adding a repo isn't always a single command.

    def onSoftwareInstallFailure(self):
        raise NotImplementedError

    def onSoftwareInstallSuccess(self):
        raise NotImplementedError

    def onSearchFailure(self):
        raise NotImplementedError

    def onSearchSuccess(self):
        raise NotImplementedError


