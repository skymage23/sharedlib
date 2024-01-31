import copy
import enum
import pathlib
import pyrsistent
import sys
import unittest.mock

#from .. import conflict_resolution
from ..conflict_resolution import ImmutableObjectWriteError as ImmutableObjectWriteError
from ..conflict_resolution import ReadOnlyAfterCommitCommittable as ReadOnlyAfterCommitCommittable

class ProjectManagementError(Exception):
    def __init__(self, message):
        super().__init__(self, "sharedlib.project_managment: Project Management Error: {0}".format(message))

class RequiredFilesystemNodeDependencyError(ProjectManagementError):
    def __init__(self, node, problem_errcode):
        self.node = node
        self.problem_errcode = problem_errcode

    def __str__(self):
        return """Problem node: {0}, Problem: {1}""".format(self.node, self.problem_errcode)


class FilesystemNodeType(enum.Enum):
    FILE = 0
    DIRECTORY = 1
    #Don't need symlink support now, but when we add it, that
    #should be a subclass of FilesystemNode in order to include symlink-specific fields.

#Immutable.
class FilesystemNode(pyrsistent.PClass):
    class CheckErrcodes(enum.Enum):
        CHECK_ERRCODE_SUCCESS = 0
        CHECK_ERRCODE_MISSING = 1
        CHECK_ERRCODE_INCORRECT_TYPE = 2

    name = pyrsistent.field(
        type=str,
        mandatory=True,
        invariant=lambda x: (
                    x not in (None, ''), 
                    'name is either None or empty.'
                    )
        )
    path = pyrsistent.field(
        #type=("pathlib.Path","unittest.mock.MagicMock"),
        mandatory=True,

        #We have to follow the "if it looks like a duck ..."
        #approach because hardcoding the expected type 
        #(pathlib.Path) is preventing us from mocking the
        #Path class for testing.
        invariant=lambda x : 
                    (
                        (
                            (x is not None) and
                            ('exists' in dir(x)) and
                            ('is_dir' in dir(x)) and
                            ('is_file' in dir(x))
                        ),
                        'path is None'
                    )
        )
    node_type = pyrsistent.field(
        type=FilesystemNodeType,
        mandatory=True,
        invariant=lambda x: (
                    x in FilesystemNodeType, 
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
            return self.CheckErrcodes.CHECK_ERRCODE_MISSING

        retval = self.CheckErrcodes.CHECK_ERRCODE_SUCCESS 
        match self.node_type:
            case FilesystemNodeType.FILE:
                if not self.path.is_file():
                    retval = self.CheckErrcodes.CHECK_ERRCODE_INCORRECT_TYPE
            case FilesystemNodeType.DIRECTORY:
                if not self.path.is_dir():
                    retval = self.CheckErrcodes.CHECK_ERRCODE_INCORRECT_TYPE

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
            #type=("pathlib.Path","unittest.mock.MagicMock"),
            mandatory=True,

            #We have to follow the "if it looks like a duck ..."
            #approach because hardcoding the expected type 
            #(pathlib.Path) is preventing us from mocking the
            #Path class for testing.
            invariant=lambda x : 
                        (
                            (
                                (x is not None) and
                                ('exists' in dir(x)) and
                                ('is_dir' in dir(x)) and
                                ('is_file' in dir(x))
                            ),
                            'path is None'
                        )
            )

        third_party_dir_name = pyrsistent.field(
            type=str,
            invariant=lambda x:(
                (x not in (None, '')),
                'third_party_dir_name is None or empty.'
                )
            )
        script_dir_name = pyrsistent.field(
            type=str,
            invariant=lambda x:(
                (x not in (None, '')),
                "script_dir_name is None or empty."
                )
            )
        source_dir_name = pyrsistent.field(
            type=str,
            invariant=lambda x:(
                (x not in (None, '')),
                'source_dir_name is None or empty.'
                )
            )

    KWARG_REQUIRED_ARGUMENTS=["name", "path"]
    ROOT_FILESYSTEM_NODE_KEY="root"
    SCRIPTS_FILESYSTEM_NODE_KEY="scripts"
    SOURCE_FILESYSTEM_NODE_KEY="source"
    THIRD_PARTY_FILESYSTEM_NODE_KEY="third_party"
    DEFAULT_SCRIPT_DIR_NAME="scripts"
    DEFAULT_THIRD_PARTY_DIR_NAME="third_party"
    DEFAULT_SOURCE_DIR_NAME="src"
    

    def onInitialize (self, **kwargs):

        name = kwargs["name"]
        path = pathlib.Path(kwargs["path"])

        self.__persistent_metadata = self.__ProjectMetadata(
            name = name,
            path = path,
            third_party_dir_name = kwargs.get("third_party_dir_name", self.DEFAULT_THIRD_PARTY_DIR_NAME),
            script_dir_name = kwargs.get("script_dir_name", self.DEFAULT_SCRIPT_DIR_NAME),
            source_dir_name = kwargs.get("source_dir_name", self.DEFAULT_SOURCE_DIR_NAME)
            )

        self.__in_workable_state = False
        self.__hard_required_filesystem_nodes={}  #These HAVE to exist. Else, the Project framework falls apart.
        self.__supplemental_filesystem_nodes={} #These CAN be required by the project itself, but not the Project framework.
        

        self.__registerRequiredFilesystemNode(
            self.ROOT_FILESYSTEM_NODE_KEY,
            path,
            FilesystemNodeType.DIRECTORY
            )


        #Required Filesystem Nodes:
        self.__registerRequiredFilesystemNode(
            self.SCRIPTS_FILESYSTEM_NODE_KEY,
            path / self.__persistent_metadata.script_dir_name,
            FilesystemNodeType.DIRECTORY,
            )


        
        self.__registerRequiredFilesystemNode(
            self.SOURCE_FILESYSTEM_NODE_KEY,
            path / self.__persistent_metadata.source_dir_name,
            FilesystemNodeType.DIRECTORY,
            )

        #Optional Filesystem Nodes 
        self.registerSupplementalFilesystemNode(
            self.THIRD_PARTY_FILESYSTEM_NODE_KEY,
            path / self.__persistent_metadata.third_party_dir_name,
            FilesystemNodeType.DIRECTORY,
            False
            )

    def onVerifyKwargs(self, **kwargs):
        #Hello
        size = len(kwargs)
        if size < len(self.KWARG_REQUIRED_ARGUMENTS):
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

        self.__hard_required_filesystem_nodes[name] = FilesystemNode(
            name = name, 
            path = path, 
            node_type = node_type, 
            required = True
            )


    def registerSupplementalFilesystemNode(
        self,
        name = None,
        path = None,
        node_type = None,
        required = False
        ):
        if self.isCommitted():
            raise ImmutableObjectWriteError()
        self.__supplemental_filesystem_nodes[name] = FilesystemNode(
            name = name, 
            path = path, 
            node_type = node_type, 
            required = required
            )

    def onCommit(self):
        if not self.__in_workable_state:
            retval = self.checkProjectTree()
            if retval is not None:
                raise conflict_resolution.CommitFailure("""
Missing optional dependencies, or optional dependencies are not of the
correct type according or project spec. If you want to force a commit,
you can work around this by calling Project.checkProjectTree() before
calling Project.commit()
""")
        self.__supplemental_filesystem_nodes = pyrsistent.freeze(self.__supplemental_filesystem_nodes)
        self.__hard_required_filesystem_nodes =  pyrsistent.freeze(self.__supplemental_filesystem_nodes)


    #If a required filesystem node is missing, we throw an exception.
    #If an optional filesystem node is missing, we just return tuple: success, arr_of_missing_paths:
    def checkProjectTree(self):
        #check_required

        supplemental_list = list(self.__supplemental_filesystem_nodes.values())
        combined_restricted_list = list(self.__hard_required_filesystem_nodes.values())
        combined_restricted_list.extend([x for x in supplemental_list if x.required == True ])


        temp_retval = None
        for var in combined_restricted_list:
            temp_retval = var.check()
            if temp_retval != FilesystemNode.CheckErrcodes.CHECK_ERRCODE_SUCCESS:
                raise RequiredFilesystemNodeDependencyError(var, temp_retval)

        self.__in_workable_state = True

        missing = None
        for var in supplemental_list:
            if not var.required:
                temp_retval = var.check()
                if temp_retval != FilesystemNode.CheckErrcodes.CHECK_ERRCODE_SUCCESS:
                    if missing is None:
                        missing = []
                    missing.append((var,temp_retval))

        return missing

    def getMetadata(self):
        return self.__persistent_metadata

    def haveThirdParty(self):
        return (self.__hard_required_filesystem_nodes[self.persistent_metadata.third_party_dir_name]).exists()

    def getThirdPartyPath(self):
        if not self.haveThirdParty():
            return None
        return self.__supplemental_filesystem_nodes[self.persistent_metadata.third_party_dir_name].path

    def getSupplementalFilesystemNodes(self):
        retval = None
        if not self.isCommitted():
            retval = copy.copy(self.__supplemental_filesystem_nodes)
        else:
            #When an object of this class is "committed",
            #the type of "self.__supplemental_filesystem_nodes"
            #changes to "PMap" (a part of Pyrsistent),
            #which automatically deep-copies itself
            #when one attempts to save a reference to it, or
            #assign it to a variable.
            retval = self.__supplemental_filesystem_nodes
            retval = pyrsistent.thaw(retval)

        return retval

    def getHardRequiredFilesystemNodes(self):
        retval = None
        if not self.isCommitted():
            retval = copy.copy(self.__hard_required_filesystem_nodes)
        else:
            #When an object of this class is "committed",
            #the type of "self.__hard_required_filesystem_nodes"
            #changes to "PMap" (a part of Pyrsistent),
            #which automatically deep-copies itself
            #when one attempts to save a reference to it, or
            #assign it to a variable.
            retval = self.__hard_required_filesystem_nodes
            retval = pyrsistent.thaw(retval)

        return retval

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
#def registerProject(
#    name = None,
#    path = None,
#    third_party_dir_name = Project.DEFAULT_THIRD_PARTY_DIR_NAME,
#    script_dir_name = Project.DEFAULT_SCRIPT_DIR_NAME,
#    source_dir_name = Project.DEFAULT_SOURCE_DIR_NAME
#    ):
#    global __current_project
#
#    if  __current_project is None:
#        __current_project = Project(
#        name = name,
#        path = path,
#        third_party_dir_name = third_party_dir_name,
#        script_dir_name = script_dir_name,
#        source_dir_name = source_dir_name
#        )
#    else:
#       raise ProjectManagementError("Only 1 current project at a time is supported at this time.")
#

#This needs to be turned into a factory to generate the current Project
#when given
def getCurrentProject():
    if __current_project is not NULL:
        return __current_project
    else:
        #Hello
