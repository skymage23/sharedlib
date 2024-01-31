import enum
import pyrsistent
from . import getters

#And if they are remoting in?
#If and when we have a GUI launch feature,
#we have that pass in a parameter telling us we
#are on a GUI. Else, we default to COMMAND_LINE.
class UIType(enum.Enum):
    COMMAND_LINE = 0
    GRAPHICAL_USER_INTERFACE = 1

class EnvType(enum.Enum):
    HOST=0
    CHROOT=1


class SoftwareInstallationFailureError(Exception):
    def __init__(self, software_name, reason=None):
        super().__init__(self, "Installation of \"{0}\" failed. Reason: \"{1}\"".format(software_name, reason))


#We want to standardize the version strings.
#major, minor, revision, misc.
#Misc. is whatever versioning info the software's
#developers are using that isn't numeric (
#1.0.2-electric-boogaloo). 
#If we must, for the version
#numbers, -1 will be used when we simply don't
#have that information.

#Getters each  have their own subclass of this to help translate
#from package manager/OS-specific versioning jargon
#to our versioning standards.

#Dependency objects CAN have their own subclass of this,
#but the default Dependency subclasses do not, and subclassing
#Dependency in the linking code is discouraged unless
#absolutely necessary. IF the dependency has their own subclass,
#that subclass will be invoked in lieu of any subclasses provided
#by the associated Getters. Thereby, extensive testing must be done
#to ensure this new Dependency subclass still works on all platforms
#to be supported by the project importing this library. Hence,
#why subclassing Dependency on your own is discouraged.
class VersionTranslator():
    class VersionTranslationError(Exception):
        def __init__(self, )
    VERSION_NUMBER_DEFAULT = -1
    def onInvocation(self):

        #returns tuple: (major, minor, revision, misc)
        raise NotImplementedError
    
    def __call__(self, str_data):
        return self.onInvocation(str_data)

class BuildEnvironment:
    class __BuildEnvironmentMetadata(pyrsistent.PClass):
        name = pyrsistent.field()
        env_type = pyrsistent.field()
        fs_path = pyrsistent.field()
        primary_getter = pyrsistent.field()
        default_ui_type = pyrsistent.field()


    #We COULD have this spawn a process to write the cache back to the file.
    #How? We have a pipe to the child process. The pipe is used as the work
    #queue.  The child takes work orders and writes their contents to the
    #cache file. Perhaps it can also take multiple work orders and bundle the
    #writes together.  If multiple installs are detected, the user will
    #be prompted, asking which one needs to be used.  This will be cached.
    #This can be prevented by the user specifying this information in a file
    #labeled "<package_name>.use"
    class __InfoCacheNode():
        def __init__(self):
            self.name = None
            self.path = None
            self.version = None
            self.id = None   #auto-generated.

    class __InfoCache():
        def __init__(self, filename):
            self.__cache_filename = filename
            self.dict = {}

        def writeBack(self):
            raise NotImplementedError

        def __sanitizeDataBeforeFileWrite(self, char_string):
            raise NotImplementedError


    def __init__(self, name, env_type, fs_path, primary_getter):
        self.__metadata = BuildEnvironmentMetadata(name, env_type, fs_path, primary_getter)

        #Hello
        self.cache = self.__open_info_cache()

    def locateBinary(self, binary_name, version):
        raise NotImplementedError

    def locateSharedLibrary(self, library_name, version = None):
        raise NotImplementedError

    def locateStaticLibrary(self, library_name, version = None):
        raise NotImplementedError

    def locateAPIHeaderFile(self, filename, version = None):
        raise NotImplementedError

    def verifySoftwareInstall(self, filename, version = None):
        raise NotImplementedError

    def attemptSoftwareInstall(self, getter=self.metadata.primary_getter):
        raise NotImplementedError

    #We TRY to request privilege escalation on a forked subprocess.
    def attemptSoftwareInstallWithElevatedPrivileges(self, getter=self.metadata.primary_getter):
        raise NotImplementedError

    #We will need this to get passwords for "sudo" and such.
    def __getUserInputPrompt(self, ui_type):
        raise NotImplementedError

    #version needs to be a tuple with two parts,
    #"major.minor.revision" and "extra crap the developer puts
    #in version strings like \"ice_cream_sandwich\"".
    def __isProperVersionIdentifier():
        raise NotImplementedError

