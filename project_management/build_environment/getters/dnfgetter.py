import dnf.cli
import pyrsistent

import .packagemanagergetter

class DnfGetter(packagemanagergetter.PackageManagementGetter):
    def getRepoConfigTemplate(self):
        raise NotImplementedError

    def onValidateRepoConfig(self):
