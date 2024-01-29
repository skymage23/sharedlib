import pyrsistent

import .
import .dependency
import .build_environment


class BinarySoftwareDependency(dependency.Dependency):
    binary_basename = field()

    def locate(self, ):
        raise NotImplementedError()

