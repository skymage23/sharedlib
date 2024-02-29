import pyrsistent

import .project_management.build_environment.getters

class RepoConfig(pyrsistent.PClass):
    package_manager = field(mandatory=True, type=str)
    name =  field(mandatory=True, type=str)
    url = field(mandatory=True, type=str)
    signing_key_url = field( mandatory=True 
            invariant=lambda data: return ((data is None) or (isinstance(data, str)))
            )

    def __init__(self):
        super().__init__()
        self.extras={}   #The config file defines options as key/value pairs.

class PackageManagerGetter(Getter):
    def __init__(self):
        raise NotImplementedError

    #We need to provide an implementation here
    #that calls package-management-option-specific option
    #validation callbacks.
    def onValidateGlobalGetterConfig(self, global_getter_config):
        raise NotImplementedError

    #Repo config: everything needed to
    #define new repo. All PackageManagementGetters
    #are required to provide a minimal, working
    #template to add a repo.
    def getRepoConfigTemplate(self):
        raise NotImplementedError

    def onValidateRepoConfig(self, repo_config):
