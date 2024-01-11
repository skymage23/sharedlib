import enum
import pathlib
import sys

class ProjectManagementError(Exception):
    def __init__(self, message):
        super().__init__(self, "sharedlib: Project Management Error {0}".format(message))

class FilesystemNode:
    class NodeType(enum.Enum):
        FILE = 0
        DIRECTORY = 1
        #Don't need symlink support now, but when we add it, that
        #should a subclass in order to include symlink-specific fields.

    def __init__(self,
                    name = None,
                    path = None,
                    node_type = None,
                    required = False
                 ):

        if name is None:
            raise ValueError("name cannot be None.")
        self.name = name

        if path is None:
            raise ValueError("path cannot be None.")
        self.path = pathlib.Path(path)

        if node_type is None:
            raise ValueError("node_type cannot be None.")

        if not node_type in NodeType:
            raise ValueError("node_type is not a valid Node Type.")
        self.node_type = node_type

        if required is None:
            raise ValueError("required cannot be None.")
        self.required = required


    def check(self):
        #Hello
        if not self.path.exists():
            return False

        retval = False 
        match self.node_type:
            case NodeType.FILE:
                retval = self.path.is_file()
            case Nodetype.DIRECTORY:
                retval = self.path.is_dir()

        return retval

    def __str__(self):
        return "Project Name: {0}\nPath: {1}\nNode Type: {2}\n\n".format(
                                                                      self.name,
                                                                      self.path,
                                                                      self.node_type
                                                                  )

#Verification is defined as all required project components existing and
#being of the correct node type on disk.

#The only optional filesystem node component we set up in the initializer
#is "third_party", and that's only because, in the future, there will
#be some useful automations we can do if we know we have a third_party
#asset directory, and where it is.

class Project
    current_project = None
    ROOT_FILESYTEM_NODE_KEY="root"
    @staticmethod
    def registerProject(
                name = None,
                path = None,
                third_party_dir_name = "third_party",
                scripts_dir_name = "scripts",
                source_dir_name = "src"
            ):
        #Name
        if Project.current_project is None:
            Project.current_project = Project(
                                      name,
                                      path,
                                      third_party_dir_name,
                                      source_dir_name
                                 )
        else:
           raise ProjectManagementError("Only 1 current project at a time is supported at this time.")
        
    def __init__(self,
                name = None,
                path = None,
                third_party_dir_name = "third_party",
                script_dir_name = "scripts",
                source_dir_name = "src",
            ):

        self.have_all_optional_nodes = False

        self.__hard_required_filesystem_nodes={}  #These HAVE to exist. Else, the Project framework falls apart.
        self.supplemental_filesystem_nodes={} #These CAN be required by the project itself, but not the Project framework.
        
        if name is None:
            raise ValueError("name cannot be none.")
        self.name = name

        if path is None:
            raise ValueError("path cannot be none.")
        self.__registerRequiredFilesystemNode(
                                   Project.ROOT_FILESYSTEM_NODE_KEY,
                                   pathlib.Path(path),
                                   FilesystemNode.NodeType.DIRECTORY
                               )



        #Required Filesystem Nodes:
        if script_dir_name is None:
            raise ValueError("script_dir_name cannot be None.")
        #self.script_dir = self.path / script_dir_name
        self.__registerRequiredFilesystemNode(
                                   script_dir_name,
                                   self.path / script_dir_name,
                                   FilesystemNode.NodeType.DIRECTORY,
                               )


        if source_dir_name is None:
            raise ValueError("source_dir_name cannot be None.")
        
        #self.source_dir = self.path / source_dir_name
        self.__registerRequiredFilesystemNode(
                                   source_dir_name,
                                   self.path / source_dir_name,
                                   FilesystemNode.NodeType.DIRECTORY,
                               )

        #Optional Filesystem Nodes 
        if not third_party_dir_name is None:
            self.registerSupplementalFilesystemNode(
                third_party_dir_name,
                self.path / third_party_dir_name,
                NodeType.DIRECTORY,
                False
            )
        else:
            raise ValueError("third_party_dir_name cannot be None.")

    def __registerRequiredFilesystemNode(self,
                                    name = None,
                                    path = None,
                                    node_type = None
                                ):
        if name is None:
            raise ValueError("name cannot be None.")


        if self.__hard_required_filesystem_nodes.get(name) is None:
            raise ValueError("Required filesystem node for name={0} has already been registered.".format(name))

       self.__hard_required_filesystem_node[name] = FilesystemNode(name, path, node_type, True)


    def registerSupplementalFilesystemNode(self,
                                      name = None,
                                      path = None,
                                      node_type = None,
                                      required = False
                                      ):
         if name is None:
             raise ValueError("name cannot be None.")

         if self.supplemental_filesystem_nodes.get(name) is None:
             raise ValueError("A supplemental filesystem node for name={0} has already been registered.".format(name))

         self.supplemental_filesystem_node[name] = FilesystemNode(name, path, node_type, required)

    def checkProjectTree(self):
        #Hell
        
        self.is_verified = True
        return True


