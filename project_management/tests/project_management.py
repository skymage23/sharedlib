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
        self.project.registerSupplementalFilesystemNode(
                                                   name = self.fs_dir_node_1_name,
                                                   path = self.fs_dir_node_1_path,
                                                   node_type = self.fs_dir_node_1_type
                                                   )

       #mock Path so that "exists" and "is_dir" succeeds:
        with mock.patch('pathlib.Path') as my_mock:
            instance = my_mock.return_value
            instance.exists.return_value = True
            instance.is_dir.return_value = True
            instance.is_file.return_value = False
            self.assertTrue(self.project.checkProjectTree() is not None)
            self.assertTrue(self.project.isUsable())

#    def test_verification_failure_missing_required(self)
#        with mock.patch('pathlib.Path') as mock:
#            instance = mock.return_value
#            instance.exists.return_value = False
#            instance.is_dir.return_value = True
#            instance.is_file.return_value = False
#            with self.assertRaises(prjmgt.RequiredFilesystemNodeMissingError):
#                self.project.checkProjectTree()

#class TestProjectFreezeSuccess(TestProjectWithSupplementalNodeInfo):
#    def setUp(self):
#        super().setUp()
#        self.project = Project(
#                          name = self.name,
#                          path = self.path,
#                          third_party_dir_name = self.third_party_dir_name,
#                          script_dir_name = self.script_dir_name,
#                          source_dir_name = self.source_dir_name
#                          )
#        self.

#class TestProjectFrameworkRequiredFSNodeLogic(TestProjectFSNodeFeatures):
#
#    def test_framework_required_exists(self):
#        with mock.patch.object(
#                    pathlib.Path,
#                    'exists',
#                    return_value=True
#                ) as mock_object:
#            self.assertTrue(self.project.checkProjectTree() is None)
#
#    def test_framework_required_does_not_exist(self):
#        #hello
#        with mock.patch.object(
#                    pathlib.Path,
#                    'exists',
#                    return_value=False
#                ) as mock_object:
#            with self.assertRaises(prjmgt.RequiredFilesystemNodeMissingError):
#                self.assertTrue(self.project.checkProjectTree(self) is not None)
#
#
#class TestProjectSupplementalFSNodeLogic(TestProjectFSNodeFeatures):
#
#    def test_supplemental_insert(self):
#        #Hello
#        self.project.registerSupplementalFilesystemNode(
#                    self.fs_node_name,
#                    self.fs_node_path,
#                    self.fs_node_type,
#                    True
#                )
#
#        self.assertEqual(len(self.project.supplemental_filesystem_nodes), 1)
#        fs_node = self.project.supplemental_filesystem_nodes.get(self.fs_node_name)
#        self.assertTrue(fs_node is not None)
#
#        self.assertEqual(fs_node.name, self.fs_node_name)
#        self.assertEqual(fs_node.path, self.fs_node_path)
#        self.assertEqual(fs_node.node_type, self.fs_node_type)
#        self.assertTrue(fs_node.required)
#
#    def test_supplemental_required_verification_exists(self):
#        #Hello
#        self.project.registerSupplementalFilesystemNode(
#                    self.fs_node_name,
#                    self.fs_node_path,
#                    self.fs_node_type,
#                    True
#                )
#
#        with mock.patch.object(
#                    pathlib.Path,
#                    'exists',
#                    return_value=True
#                ) as mock_object:
#            self.assertTrue(self.project.checkProjectTree() is None)
#
#    def test_supplemental_required_verification_does_not_exist(self): 
#        #Hello
#        self.project.registerSupplementalFilesystemNode(
#                    self.fs_node_name,
#                    self.fs_node_path,
#                    self.fs_node_type,
#                    True
#                )
#
#        with mock.patch.object(
#                    pathlib.Path,
#                    'exists',
#                    return_value=True
#                ) as mock_object:
#            with self.assertRaises(prjmgt.RequiredFilesystemNodeMissingError):
#                self.assertTrue(self.project.checkProjectTree() is not None)
#
#    def test_supplemental_optional_verification_exists(self):
#        #Hello
#        self.project.registerSupplementalFilesystemNode(
#                    self.fs_node_name,
#                    self.fs_node_path,
#                    self.fs_node_type,
#                    False
#                )
#
#        with mock.patch.object(
#                    pathlib.Path,
#                    'exists',
#                    return_value=True
#                ) as mock_object:
#            self.assertTrue(self.project.checkProjectTree() is None)
#
#    def test_supplemental_optional_verification_does_not_exist(self):
#        #Hello
#        self.project.registerSupplementalFilesystemNode(
#                    self.fs_node_name,
#                    self.fs_node_path,
#                    self.fs_node_type,
#                    False
#                )
#
#        with mock.patch.object(
#                    pathlib.Path,
#                    'exists',
#                    return_value=True
#                ) as mock_object:
#            with self.assertRaises(prjmgt.RequiredFilesystemNodeMissingError):
#                self.assertTrue(self.project.checkProjectTree() is not None)


if __name__ == "__main__":
    unittest.main()
