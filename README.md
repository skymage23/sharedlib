# sharedlib
Shared Python library containing code shared across at least a couple of my other projects. Rather than rewriting common logic, I've decided to put all that code in a separate library.

# Weird class method naming:
You may notice that this library, in its base class definitions, uses a mixture of callbacks and traditional method overwritting.
I did this on purpose.  Callbacks are used when logic needs to be injected at certain points, but the call order must be kept static.
For example, you should always verify your input for ReadOnlyAfterCommitCommitables BEFORE you use them in onCommit().

