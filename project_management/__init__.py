import copy
import enum
import pathlib
import pyrsistent
import sys

from . import conflict_resolution.ImmutableObjectWriteError as ImmutableObjectWriteError
from . import conflict_resolution.ReadOnlyAfterCommitCommittable as ReadOnlyAfterCommitCommittable

class ProjectManagementError(Exception):
    def __init__(self, message):
        super().__init__(self, "sharedlib.project_managment: Project Management Error: {0}".format(message))

class RequiredFilesystemNodeMissingError(ProjectManagmentError):
    def __init__(self, node):
        super().__init__(self, """Missing required filesystem node:

                         {0}

                         """.format(node))


class FilesystemNodeType(enum.Enum):
    FILE = 0
    DIRECTORY = 1
    #Don't need symlink support now, but when we add it, that
    #should be a subclass of FilesystemNode in order to include symlink-specific fields.

#Immutable.
class FilesystemNode(pyrsistent.PClass):

    name = pyrsistent.field(
                       type=str,
                       mandatory=True,
                       invariant=lambda x: (
                                   x not in (None, ''), 
                                   'name is either None or empty.'
                                   )
                       )
    path = pyrsistent.field(
                       type=pathlib.Path,
                       mandatory=True,
                       invariant=lambda x :(
                                   #Hello
                                   (x is not None),
                                   'path is None'
                                   )
                       )
    node_type = pyrsistent.field(
                            type=FilesystemNodeType,
                            mandatory=True,
                            invariant=lamda x: (
                                        x in project_management.FilesystemNodeType, 
                                        'node_type is not a valid member of FileNodeType'
                                        )
                            )
    required = pyrsistent.field(
                           type=bool,
                           mandatory=True,
                           invariant=lambda x:(
                                       (x is not None),
                                       'required is None'
                                       )
                           )

    
    def check(self):
        if not self.path.exists():
            return False

        retval = False 
        match self.node_type:
            case FilesystemNodeType.FILE:
                retval = self.path.is_file()
            case FilesystemNodeType.DIRECTORY:
                retval = self.path.is_dir()

        return retval

    def __str__(self):
        return """
        Node Name: {0}
        Path: {1}
        Node Type: {2}
        """.format(self.name, self.path, self.node_type)



class Project(ReadOnlyAfterCommitCommittable):
  
    class __ProjectMetadata(pyrsistent.PClass):
        name = pyrsistent.field(
                           type=str,
                           invariant=lambda x:(
                                       (x not in (None, '')),
                                       'name is None or empty.'
                                       )
                           )
        path = pyrsistent.field(
                           type=str,
                           invariant=lambda x:(
                                       (),
                                       'name is None or empty'
                                       )
                           )

        third_party_dir_name = pyrsistent.field(
                                           type=str,
                                           invariant=lambda x:(
                                                       (x is not in (None, '')),
                                                       'third_party_dir_name is None or empty.'
                                                       )
                                           )
        script_dir_name = pyrsistent.field(
                                      type=str,
                                      invariant=lambda x:(
                                                  (x is not in (None, '')),
                                                  "script_dir_name is None or empty."
                                                  )
                                      )
        source_dir_name = pyrsistent.field(
                                      type=str,
                                      invariant=lambda x:(
                                                  (x is not in (None, '')),
                                                  'source_dir_name is None or empty.'
                                                  )
                                      )

    KWARG_REQUIRED_ARGUMENTS=["name", "path"]
    ROOT_FILESYSTEM_NODE_KEY="root"
    DEFAULT_SCRIPT_DIR_NAME="scripts"
    DEFAULT_THIRD_PARTY_DIR_NAME="third_party"
    DEFAULT_SOURCE_DIR_NAME="src"
    

    def onInitialize (self, **kwargs):

        name = kwargs["name"]
        path = pathlib.Path(kwargs["path"])

        self.__persistent_metadata = self.__ProjectMetadata(
                                         name,
                                         path,
                                         kwargs.get("third_party_dir_name", self.DEFAULT_THIRD_PARTY_DIR_NAME),
                                         kwargs.get("script_dir_name", self.DEFAULT_SCRIPT_DIR_NAME),
                                         kwargs.get("source_dir_name", self.DEFAULT_SOURCE_DIR_NAME)
                                         )

        self.__in_workable_state = False
        self.__hard_required_filesystem_nodes={}  #These HAVE to exist. Else, the Project framework falls apart.
        self.__supplemental_filesystem_nodes={} #These CAN be required by the project itself, but not the Project framework.
        

        self.__registerRequiredFilesystemNode(
                                                 self.ROOT_FILESYSTEM_NODE_KEY,
                                                 path,
                                                 FilesystemNodeType.DIRECTORY
                                             )

        rootNode = self.__hard_required_filesystem_nodes[self.ROOT_FILESYSTEM_NODE_KEY]


        #Required Filesystem Nodes:
        self.__registerRequiredFilesystemNode(
                                                 self.persistent_metadata.script_dir_name,
                                                 path / self.__persistent_metadata.script_dir_name,
                                                 FilesystemNodeType.DIRECTORY,
                                             )


        
        self.__registerRequiredFilesystemNode(
                                                 self.persistent_metadata.source_dir_name,
                                                 path / self.__persistent_metadata.source_dir_name,
                                                 FilesystemNodeType.DIRECTORY,
                                             )

        #Optional Filesystem Nodes 
        self.registerSupplementalFilesystemNode(
                                                   self.persistent_metadata.third_party_dir_name,
                                                   path / self.__persistent_metadata.third_party_dir_name,
                                                   FilesystemNodeType.DIRECTORY,
                                                   False
                                               )

    def onVerifyKwargs(self, **kwargs):
        #Hello
        size = len(kwargs)
        if size < self.KWARG_ARGUMENT_REQUIRED_COUNT:
            raise ReadOnlyAfterCommitCommittable.KwargVerificationError("Too few arguments")

        for var in self.KWARG_REQUIRED_ARGUMENTS:
            if not var in kwargs:
                raise ReadOnlyAfterCommitCommittable.KwargVerificationError("Missing required argument: {0}".format(var))
        return True
    def __str__(self):
        buffer=[]
        buffer.append("""
        Project.registerProject:
        name:                  {0},
        path:                  {1},

        """.format(self.__persistent_metadata.name, self.__persistent_metadata.path))

        if not isinstance(required_nodes, pyrsistent.PMap):
            required_nodes = copy.copy(self.__hard_required_filesystem_nodes)

        #Keep in mind that PMap is going to quietly create a new list structure here containing a deep copy
        #of "required_nodes" in addition to the results of the list comprehension.
        required_nodes.append([x for x in self.__supplemental_filesystem_nodes if x.required == True])

        buffer.append('********************Required Filesystem Nodes********************')
        for var in required_nodes:
            buffer.append(var.__str__())

        required_nodes = None
        buffer.append('*******************Supplemental Filesystem Nodes********************')
        buffer.append([x.__str__() for x in self.__supplemental_filesystem_nodes if x.required == False])

        return("""
        """.join(buffer))




    def __registerRequiredFilesystemNode(
                                            self,
                                            name = None,
                                            path = None,
                                            node_type = None
                                        ):
        if self.isCommitted():
            raise ImmutableObjectWriteError()
        self.__hard_required_filesystem_nodes[name] = FilesystemNode(name, path, node_type, True)


    def registerSupplementalFilesystemNode(
                                              self,
                                              name = None,
                                              path = None,
                                              node_type = None,
                                              required = False
                                          ):
         if self.isCommitted():
             raise ImmutableObjectWriteError()
         self.__supplemental_filesystem_nodes[name] = FilesystemNode(name, path, node_type, required)

    def onCommit(self):
        super().commit()
        if not self.__in_workable_state:
            self.checkProjectTree()
        self.__supplemental_filesystem_nodes = pyrsistent.freeze(self.__supplemental_filesystem_nodes)
        self.__hard_required_filesystem_nodes  pyrsistent.freeze(self.__supplemental_filesystem_nodes)


    #If a required filesystem node is missing, we throw an exception.
    #If an optional filesystem node is missing, we just return tuple: success, arr_of_missing_paths:
    def checkProjectTree(self):
        #check_required
        for var in self.__hard_required_filesystem_nodes:
            if not var.exists():
               raise RequiredFilesystemNodeMissingError(var)

        missing = None
        found_missing = False
        for var in self.__supplemental_filesystem_nodes:
            if not var.check():
                if var.required:
                    raise RequiredFilesystemNodeMissingError(var)
                found_missing = True
                if missing is None:
                    missing = []
                missing.append(var.path)

        self.__in_workable_state = True
        return missing

    def getMetadata(self):
        return self.__persistent_metadata

    def haveThirdParty(self):
        return (self.__hard_required_filesystem_nodes[self.persistent_metadata.third_party_dir_name]).exists()

    def getThirdPartyPath(self):
        if not self.haveThirdParty():
            return None
        return self.__supplemental_filesystem_nodes[self.persistent_metadata.third_party_dir_name].path

    def getSupplementalFilesystemNodes():
        return copy.copy(self.__supplemental_filesystem_nodes)



    #Useful if we need to prevent anything else from using the Project while
    #we prepare the filesystem in some way, like installing dependencies.

    #If you use this and don't make sure nothing else is attempting to use the Project
    #object to affect the project on the filesystem, you may very well break things
    #and it will be your fault, not the fault of this library's developers.

    #The only way to set usability back to True is to call "checkProjectTree"
    #to run a check of the project filesystem to make sure all dependencies
    #are still in place.
    def setUsabilityFalse(self):
        self.__in_workable_state = False

    def isUsable(self):
        return self.__in_workable_state

__current_project = None
def registerProject(
                       name = None,
                       path = None,
                       third_party_dir_name = DEFAULT_THIRD_PARTY_DIR_NAME,
                       script_dir_name = DEFAULT_SCRIPT_DIR_NAME,
                       source_dir_name = DEFAULT_SOURCE_DIR_NAME
                   ):

    if __current_project is None:
        __current_project = Project(
                                  name,
                                  path,
                                  third_party_dir_name,
                                  script_dir_name,
                                  source_dir_name
                             )
    else:
       raise ProjectManagementError("Only 1 current project at a time is supported at this time.")

def getCurrentProject():
    return __current_project
