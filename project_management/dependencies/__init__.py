import enum

class DependencyTimings(enum.Enum):
    BUILD  = 0
    RUNTIME = 1

class DependencyTypes(enum.Enum):
    FILESYSTEM_NODE=0
    STATIC_LIBRARY=1
    SHARED_LIBRARY=2
    PROGRAM=3



