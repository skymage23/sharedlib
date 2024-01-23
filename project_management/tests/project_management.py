#!/usr/bin/env python3
import inspect
import pathlib
import sys
import unittest

from unittest import mock as mock

our_path = pathlib.Path(inspect.stack()[0][1])
import_path = our_path.parent.parent.parent.parent
sys.path.append(import_path.__str__())

from sharedlib import project_management as prjmgt
from sharedlib import conflict_resolution

class TestProjectFramework(unittest.TestCase):
    def setUp(self):
        self.name = "Test"
        self.path = pathlib.Path("./testclasscreation")
        self.scripts_dir_name = "scripts"
        self.source_dir_name = "src"
        self.third_party_dir_name = "third_party"

class TestProjectClassCreation(TestProjectFramework):

    def wasProjectCreatedCorrectly(self, project=None):
        if project is None:
            raise ValueError("project cannot be None")

        metadata = project.getMetadata()
        self.assertTrue(metadata.name == self.name)
        self.assertTrue(metadata.path == pathlib.Path(self.path))


        required_keys = [
                project.ROOT_FILESYSTEM_NODE_KEY,
                project.THIRD_PARTY_FILESYSTEM_NODE_KEY,
                project.SCRIPTS_FILESYSTEM_NODE_KEY,
                project.SOURCE_FILESYSTEM_NODE_KEY
                ]

        required_values = {
                    project.ROOT_FILESYSTEM_NODE_KEY: self.path,
                    project.THIRD_PARTY_FILESYSTEM_NODE_KEY: self.path / self.third_party_dir_name,
                    project.SCRIPTS_FILESYSTEM_NODE_KEY: self.path / self.scripts_dir_name,
                    project.SOURCE_FILESYSTEM_NODE_KEY: self.path / self.source_dir_name
                }

        self.assertFalse(project.isCommitted())

        hard_required = project.getHardRequiredFilesystemNodes()
        self.assertTrue(len(hard_required) > 0)

        supplemental = project.getSupplementalFilesystemNodes()
        self.assertTrue(len(supplemental) > 0)

        nodes = {**hard_required, **supplemental}
        for var in required_keys:
            self.assertTrue(nodes[var], required_values[var])

    def test_create(self):
        #Hello:
        proj = prjmgt.Project(
                                 name = self.name,
                                 path = self.path,
                                 third_party_dir_name = self.third_party_dir_name,
                                 script_dir_name = self.scripts_dir_name,
                                 source_dir_name  = self.source_dir_name
                             )

        self.wasProjectCreatedCorrectly(proj)

    def testRegisterProject(self):
        prjmgt.registerProject(
                              self.name,
                              self.path,
                              self.third_party_dir_name,
                              self.scripts_dir_name,
                              self.source_dir_name
                          )
        self.wasProjectCreatedCorrectly(prjmgt.getCurrentProject())

class TestProjectClass(TestProjectFramework):
    def setUp(self):
        super().setUp()
        self.project = prjmgt.Project(
                name = self.name, 
                path = self.path, 
                script_dir_name = self.scripts_dir_name, 
                source_dir_name = self.source_dir_name
                )
    def tearDown(self):
        self.project = None

class TestProjectClassWithSupplementalNodeInfo(TestProjectClass):
    def setUp(self):
        super().setUp()

        self.fs_dir_node_1_name = "DirNode1"
        self.fs_dir_node_1_path = pathlib.Path("./dir_node1")
        self.fs_dir_node_1_type = prjmgt.FilesystemNodeType.DIRECTORY

        self.fs_dir_node_2_name = "DirNode2"
        self.fs_dir_node_2_path = pathlib.Path("./dir_node2")
        self.fs_dir_node_2_type = prjmgt.FilesystemNodeType.DIRECTORY

        self.fs_file_node_1_name = "FileNode1"
        self.fs_file_node_1_path = pathlib.Path("./file_node1")
        self.fs_file_node_1_type = prjmgt.FilesystemNodeType.FILE


class TestProjectFSNodeFeatures(TestProjectClassWithSupplementalNodeInfo):
    
    def test_success(self):
        self.project.registerSupplementalFilesystemNode(
                                                   name = self.fs_dir_node_1_name,
                                                   path = self.fs_dir_node_1_path,
                                                   node_type = self.fs_dir_node_1_type,
                                                   required=True
                                                   )
        supplemental = self.project.getSupplementalFilesystemNodes()
        node = supplemental.get(self.fs_dir_node_1_name)
        self.assertTrue(node is not None)
        self.assertTrue(node.name == self.fs_dir_node_1_name)
        self.assertTrue(node.path == self.fs_dir_node_1_path)
        self.assertTrue(node.node_type == self.fs_dir_node_1_type)
        self.assertTrue(node.required == True)

class TestProjectVerificationLogic(TestProjectClassWithSupplementalNodeInfo):

    def test_verifications_success(self):
        with mock.patch('pathlib.Path') as MockPath:
            instance = MockPath.return_value
            instance.exists.return_value=True
            instance.is_dir.return_value=True
            instance.is_file.return_value=False
            instance.__truediv__.return_value=pathlib.Path()


            project = prjmgt.Project(
                    name = self.name, 
                    path = pathlib.Path(self.path.__str__()),  #Otherwise, we can't mock this path object 
                    script_dir_name = self.scripts_dir_name, 
                    source_dir_name = self.source_dir_name
                    )

            project.registerSupplementalFilesystemNode(
                                                       name = self.fs_dir_node_1_name,
                                                       path = pathlib.Path(self.fs_dir_node_1_path.__str__()),
                                                       node_type = self.fs_dir_node_1_type
                                                       )

            self.assertFalse(project.isUsable())
            retval = project.checkProjectTree()
            self.assertTrue(retval is None)
            self.assertTrue(project.isUsable())

    def test_verification_failure_missing_required(self):
        with mock.patch('pathlib.Path') as MockPath:
            instance = MockPath.return_value
            instance.exists.return_value=False
            instance.is_dir.return_value=True
            instance.is_file.return_value=False
            instance.__truediv__.return_value=pathlib.Path()


            project = prjmgt.Project(
                    name = self.name, 
                    path = pathlib.Path(self.path.__str__()),  #Otherwise, we can't mock this path object 
                    script_dir_name = self.scripts_dir_name, 
                    source_dir_name = self.source_dir_name
                    )

            project.registerSupplementalFilesystemNode(
                                                       name = self.fs_dir_node_1_name,
                                                       path = self.fs_dir_node_1_path,
                                                       node_type = self.fs_dir_node_1_type
                                                       )

            try:
                retval = project.checkProjectTree()
                print(retval)
                self.assertTrue(retval is None)
            except prjmgt.RequiredFilesystemNodeDependencyError as err:
                self.assertEqual(err.problem_errcode, prjmgt.FilesystemNode.CheckErrcodes.CHECK_ERRCODE_MISSING)


    def test_verification_failure_missing_incorrect_type(self):
        with mock.patch('pathlib.Path') as MockPath:
            instance = MockPath.return_value
            instance.exists.return_value=True
            instance.is_dir.return_value=False
            instance.is_file.return_value=False
            instance.__truediv__.return_value=pathlib.Path()


            project = prjmgt.Project(
                    name = self.name, 
                    path = pathlib.Path(self.path.__str__()),  #Otherwise, we can't mock this path object 
                    script_dir_name = self.scripts_dir_name, 
                    source_dir_name = self.source_dir_name
                    )

            project.registerSupplementalFilesystemNode(
                                                       name = self.fs_dir_node_1_name,
                                                       path = self.fs_dir_node_1_path,
                                                       node_type = self.fs_dir_node_1_type
                                                       )

            try:
                retval = project.checkProjectTree()
                print(retval)
                self.assertTrue(retval is None)
            except prjmgt.RequiredFilesystemNodeDependencyError as err:
                self.assertEqual(err.problem_errcode, prjmgt.FilesystemNode.CheckErrcodes.CHECK_ERRCODE_INCORRECT_TYPE)

    #Differs in that we don't throw an exception for missing,
    #non-required dependencies. Instead, we just return a list
    #of missing dependencies.
    def test_verification_failure_optional_missing (self):
        with mock.patch('pathlib.Path') as MockPath:
            instance = MockPath.return_value
            instance.exists.return_value=True
            instance.is_dir.return_value=True #All hard-required dependencies are currently directories.
            instance.is_file.return_value=False
            instance.__truediv__.return_value=pathlib.Path()


            project = prjmgt.Project(
                    name = self.name, 
                    path = pathlib.Path(self.path.__str__()),  #Otherwise, we can't mock this path object 
                    script_dir_name = self.scripts_dir_name, 
                    source_dir_name = self.source_dir_name
                    )

            project.registerSupplementalFilesystemNode(
                                                       name = "TestFile",
                                                       path = pathlib.Path("test_file"),
                                                       node_type = prjmgt.FilesystemNodeType.FILE
                                                       )

            retval = project.checkProjectTree()
            self.assertTrue(retval is not None)
            self.assertEqual(retval[0][0].name, "TestFile")
            self.assertEqual(retval[0][1], prjmgt.FilesystemNode.CheckErrcodes.CHECK_ERRCODE_INCORRECT_TYPE)

class TestProjectRecordPersistence(TestProjectClassWithSupplementalNodeInfo):
    def setUp(self):
        super().setUp()
        self.project = prjmgt.Project(
                          name = self.name,
                          path = self.path,
                          third_party_dir_name = self.third_party_dir_name,
                          script_dir_name = self.scripts_dir_name,
                          source_dir_name = self.source_dir_name
                          )
    def tearDown(self):
        self.project = None

    def test_project_object_persistence(self):
        #Because we are using PClass from Pyrsistent,
        #fields on the metadata are immutable and we SHOULD
        #get an AttributeError thrown at us when we try to
        #change their value.
        with self.assertRaises(AttributeError):
            metadata_copy = self.project.getMetadata()
            metadata_copy.name = "Ham"
            self.assertNotEqual(metadata_copy.name, self.project.getMetadata().name)


    def test_project_filesystem_node_object_persistence(self):
        #Because we are using PClass from Pyrsistent,
        #fields on the filesystem node records are immutable and we SHOULD
        #get an AttributeError thrown at us when we try to
        #change their value.
        with self.assertRaises(AttributeError):
            hard_required_list_copy = self.project.getHardRequiredFilesystemNodes()
            hard_required_list_copy["root"].name = "Ham"
            self.assertNotEqual(
                    hard_required_list_copy.name,
                    (self.project.getHardRequiredFilesystemNodes())[0].name
                    )

    def  test_hard_required_filesystem_node_list_persistence_pre_commit(self):
         key = prjmgt.Project.ROOT_FILESYSTEM_NODE_KEY
         copy = self.project.getHardRequiredFilesystemNodes()
         copy.pop(key)
         self.assertTrue((self.project.getHardRequiredFilesystemNodes()).get(key, None) is not None)

    def  test_supplemental_filesystem_node_list_persistence_pre_commit(self):
         key = prjmgt.Project.THIRD_PARTY_FILESYSTEM_NODE_KEY
         copy = self.project.getSupplementalFilesystemNodes()
         copy.pop(key)
         self.assertTrue((self.project.getSupplementalFilesystemNodes()).get(key, None) is not None)

class TestProjectCommit(TestProjectClassWithSupplementalNodeInfo):

    def test_commit_success(self):
        with mock.patch('pathlib.Path') as MockPath:
            instance = MockPath.return_value
            instance.exists.return_value=True
            instance.is_dir.return_value=True
            instance.is_file.return_value=False
            instance.__truediv__.return_value=pathlib.Path()


            project = prjmgt.Project(
                    name = self.name, 
                    path = pathlib.Path(self.path.__str__()),  #Otherwise, we can't mock this path object 
                    script_dir_name = self.scripts_dir_name, 
                    source_dir_name = self.source_dir_name
                    )



            self.assertFalse(project.isUsable())
            project.commit()
            self.assertTrue(project.isUsable())


            with self.assertRaises(conflict_resolution.ImmutableObjectWriteError):
                project.registerSupplementalFilesystemNode(
                                                           name = self.fs_dir_node_1_name,
                                                           path = pathlib.Path(self.fs_dir_node_1_path.__str__()),
                                                           node_type = self.fs_dir_node_1_type
                                                           )
            self.assertEqual(len(project.getSupplementalFilesystemNodes().values()), 1) #third_party, only

    #Make sure that freezing doesn't break dict persistence:
    def test_commit_fs_node_dicts_freeze_required_success(self):
        with mock.patch('pathlib.Path') as MockPath:
            instance = MockPath.return_value
            instance.exists.return_value=True
            instance.is_dir.return_value=True
            instance.is_file.return_value=False
            instance.__truediv__.return_value=pathlib.Path()


            project = prjmgt.Project(
                    name = self.name, 
                    path = pathlib.Path(self.path.__str__()),  #Otherwise, we can't mock this path object 
                    script_dir_name = self.scripts_dir_name, 
                    source_dir_name = self.source_dir_name
                    )

            project.commit()

            key = prjmgt.Project.ROOT_FILESYSTEM_NODE_KEY
            copy = self.project.getHardRequiredFilesystemNodes()
            copy.pop(key)
            self.assertTrue((self.project.getHardRequiredFilesystemNodes()).get(key, None) is not None)


    def test_commit_fs_node_dicts_freeze_required_success(self):
        with mock.patch('pathlib.Path') as MockPath:
            instance = MockPath.return_value
            instance.exists.return_value=True
            instance.is_dir.return_value=True
            instance.is_file.return_value=False
            instance.__truediv__.return_value=pathlib.Path()


            project = prjmgt.Project(
                    name = self.name, 
                    path = pathlib.Path(self.path.__str__()),  #Otherwise, we can't mock this path object 
                    script_dir_name = self.scripts_dir_name, 
                    source_dir_name = self.source_dir_name
                    )

            project.commit()

            key = prjmgt.Project.THIRD_PARTY_FILESYSTEM_NODE_KEY
            copy = self.project.getSupplementalFilesystemNodes()
            copy.pop(key)
            self.assertTrue((self.project.getSupplementalFilesystemNodes()).get(key, None) is not None)

if __name__ == "__main__":
    unittest.main()
