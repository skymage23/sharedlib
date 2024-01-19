#!/usr/bin/env python3
import inspect
import pathlib
import sys
import unittest

from unittest import mock

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

        self.assertFalse(project.committed)
        self.assertEqual(
                            project.third_party_dir_name, 
                            self.third_party_dir_name
                        )


        self.assertEqual(
                len(project._hard_required_filesystem_nodes), 
                3
                )

        #We only need to check 1 of the requirements set in the initializer,
        #because if at least 1 works, so will all the others.
        node=project._hard_required_filesystem_nodes[self.scripts_dir_name]
        self.assertEqual(node.name, self.scripts_dir_name)
        self.assertEqual(node.path, self.path / self.scripts_dir_name)
        self.assertEqual(node.node_type, prjmgt.FilesystemNodeType.DIRECTORY)
        
        #No, the Project object is not usable after
        #being created. You need to check the filesystme
        #first to make sure all dependencies are in place
        #using the checkProjectTree method. Readiness is
        #tracked using an internal variable called
        #"__in_workable_state".
        self.assertFalse(project._in_workable_state)

    def test_create(self):
        #Hello:
        proj = prjmgt.Project(
                                 self.name,
                                 self.path,
                                 self.third_party_dir_name,
                                 self.scripts_dir_name,
                                 self.source_dir_name
                             )

        self.wasProjectCreatedCorrectly(proj)

    def testRegisterProject(self):
        prjmgt.Project.registerProject(
                                  self.name,
                                  self.path,
                                  self.third_party_dir_name,
                                  self.scripts_dir_name,
                                  self.source_dir_name
                              )
        self.wasProjectCreatedCorrectly(prjmgt.Project._current_project)

#class TestProjectFSNodeFeatures(TestProjectFramework):
#    def setUp(self):
#        super().setUp()
#        self.project = prjmgt.Project(
#                self.name, 
#                self.path, 
#                self.scripts_dir_name, 
#                self.source_dir_name
#                )
#
#        self.fs_node_name = "Node1"
#        self.fs_node_path = "./node1"
#        self.fs_node_type = prjmgt.FilesystemNodeType.DIRECTORY
#
#    def tearDown(self):
#        self.project = None
#
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
