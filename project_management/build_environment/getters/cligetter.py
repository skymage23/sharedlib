from . import getters
from . import loggers

class CLIGetter(getters.Getter):
    class GetterCommands(enum.Enum):
       INVALID,
       SEARCH,
       VERIFY_INSTALL,
       INSTALL

    def __init__(self, command_start = None, logger = None):
        if command_name is None:
            raise ValueError("\"command_name\" is None.")
        if logger is None:
            raise ValueError("logger cannot be None.")
        self.command_start = command_start
        self.logger = logger
        
    #This may seem a bit silly, but it better handles shared arguments.
    def __construct_command(self, command: GetterCommand = GetterCommand.INVALID, args={}):
        self.__validate_getter_command(command)
        temp_retval

        command_buffer = [self.command_start]
        self.__construct_command_parameters_prefix(command_buffer)
        temp_retval = self.__construct_command_parameters_body(command_buffer, command, args)
        

        self.__construct_command_parameters_postfix(command_buffer)
        return ' '.join(command_buffer)
        #retval

    def validate_getter_command(command: GetterCommand = GetterCommand.INVALID):
        return (command != GetterCommand.INVALID)

    def construct_command_body(self, command_buffer, command: GetterCommand, args={}):
        

    def construct_command_parameters_prefix(self, command_buffer):
        pass

    def construct_command_parameters_postfix(self, command_buffer):
        pass

    def construct_command_search(self, command_buffer):
        raise NotImplementedError

    def construct_command_install(self, command_buffer):
        raise 
    
    def __run_command(self, cli_command, logger):
        raise NotImplementedError

    def search(self, search_term):
        term = self.construct_getter_search_term()
        command = self.construct_command(GetterCommand.SEARCH, args={"term": term})
        self.run_command(command)

    def verifyInstall(self, dependency_metadata):
        command = self.construct_command(GetterCommands.VERIFY_INSTALL, args={"metadata": dependency_metadata})
        self.run_command(command)
