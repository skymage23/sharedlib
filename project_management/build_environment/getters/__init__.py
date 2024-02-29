from .error_checking import validation

#We use a mixture of callbacks and method overloads in order
#to force sane operation with input validation.
#This is to create a consistent usage experience for code
#utilizing subclasses of "Getter". Things that need to happen
#at specific times happen, and those that can happen whenever,
#we just use regular method overloading.



class GetterSearchResult:
    def __init__(self, search_term, package_name):
        self.search_term
        self.package_name

#What is getting passed from the Dependency
#to the Getter via the BuildEnvironment?
#package name (map applied) and version.


class Getter:
    #Hello
    def __init__(self, build_environment, global_getter_config):
        self.build_env = build_environment
        #Hello

    def onValidateGlobalGetterConfig(self, global_getter_config):
        raise NotImplementedError


    #Retures a string to be used as the parameter to
    #"search".  Could be a regex, could be just a package
    #name. It depends on the Getter subclass, the
    #dependency, and user specifications.
    def buildSearchTermForDependency(self, dependency_metadata, include_version=True):
        raise NotImplementedError

    def search(self, search_term):
        raise NotImplementedError

    def verifyInstall(self, dependency_metadata):
        raise NotImplementedError


    def onInstall(self, install_parameters):
        raise NotImplementedError

    #OK. What is validation fails?
    #Well, then we return an array of <__>.
    def onValidateInstallParameters(self, install_parameters):
        raise NotImplementedError

    def generateInstallParameters(self):
        raise NotImplementedError

    def install(self):
        if not onValidateInstallParameters():  
            raise validation.ParameterValidationError():
