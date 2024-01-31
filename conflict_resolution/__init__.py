import pyrsistent
from .error_handling import validation

class ImmutableObjectWriteError(Exception):
    def __init__(self):
        super().__init__("sharedlib.conflict_resolution: You have attempted to write to an immutable, read-only object.")

class DoubleCommitError(Exception):
    def __init__(self):
        super().__init__("sharedlib.conflict_resolution: You have attempted to multiple commits on an object that only allows one commit.")

class CommitFailureError(Exception):
    def __init__(self, message):
        super().__init__("Commit failed: {0}".format(message))


#Committable is for when object state needs
#to be snapshotted in some way, shape, or form.
#Exactly what it means to commit an object depends
#on the object's class.
class Committable:
    def commit(self):
        pass

#The difference between this and Freezable is semantics.
#This class is for when modifications in regards to the
#business logic implemented in subclasses must or
#to any held data must be made prior to freezing.

#The class name is TO SET EXPECTATIONS ONLY.
#It does not implement immutability! 
#It can't without knowing the requirements of
#the usecase. It is up to the developers
#of the subclasses to implement immutability.
class ReadOnlyAfterCommitCommittable(Committable):

    class InitializationCallbackMissingError(Exception):
        def __init__(self):
            super().__init__("sharedlib.conflict_resolution.ReadOnlyAfterCommitCommittable: onIntialization callback missing.")
    
    class KwargValidationCallbackMissingError(Exception):
        def __init__(self):
            super().__init__("sharedlib.conflict_resolution.ReadOnlyAfterCommitCommittable: onKwargVerification callback missing.")
    
    class KwargValidationError(validation.ParameterValidationError):
        def __init__(self, message):
            super().__init__("sharedlib.conflict_resolution.ReadOnlyAfterCommitCommittable: kwarg verification failed. Reason: {0}".format(message))


    def __init__(self, **kwargs):
        super().__init__()
        self.__ro_committable_metadata = {}
        self.__ro_committable_metadata["committed"] = False

        if self.onValidateKwargs(**kwargs):
           self.onInitialize(**kwargs)
        else:
            raise self.KwargValidationError("onValidateKwargs returned False, indicating general failure.")

    def commit(self):
        if self.__ro_committable_metadata["committed"] == True:
            raise DoubleCommitError()

        self.onCommit()
        self.__ro_committable_metadata["committed"] = True
        self.__ro_committable_metadata = pyrsistent.freeze(self.__ro_committable_metadata)

    #Keep people from shooting themselves in the foot.
    def onValidateKwargs(self, **kwargs):
        raise self.KwargValidationCallbackMissingError()

    def onInitialize(self, **kwargs):
        raise self.InitializationCallbackMissingError()


    #If the user isn't overwritting this, we just assume they don't have any logic
    #to run per-commit.
    def onCommit(self):
        pass

    def isCommitted(self):
        return self.__ro_committable_metadata["committed"]

    def isReadOnly(self):
        return self.isCommitted()
