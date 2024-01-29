import inspect
import pathlib
import sys
import unittest

from unittest import mock as mock
our_path = pathlib.Path(inspect.stack()[0][1])
import_path = our_path.parent.parent.parent.parent.parent
sys.path.append(import_path.__str__())

from sharedlib.project_management import build_environment as bldenv


class TestCacheBuildEnvironment(bldenv.BuildEnvironment):
    def __init__():
