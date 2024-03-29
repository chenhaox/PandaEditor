from abc import ABC, abstractmethod
from editor.utils import try_execute as safe_execute


class Command(ABC):
    """Base abstract Command class"""

    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def do(self, *args, **kwargs):
        return

    @abstractmethod
    def undo(self, *args, **kwargs):
        return

    @abstractmethod
    def clean(self, **kwargs):
        pass


class CommandManager(object):
    def __init__(self, max_commands=30):
        """count = max number of commands to save"""

        self.undo_commands = []
        self.redo_commands = []
        self.max_commands = max_commands

    def push_undo_command(self, command):
        """Push the given command to the undo command stack."""
        self.undo_commands.append(command)

        if len(self.undo_commands) > self.max_commands:
            cmd = self.undo_commands[0]
            cmd.clean()
            self.undo_commands.remove(cmd)

    def pop_undo_command(self):
        """Remove the last command from the undo command stack and return it.
        If the command stack is empty, EmptyCommandStackError is raised.
        """
        try:
            last_undo_command = self.undo_commands.pop()
        except IndexError:
            last_undo_command = None
        return last_undo_command

    def push_redo_command(self, command):
        """Push the given command to the redo command stack."""
        self.redo_commands.append(command)

    def pop_redo_command(self):
        """Remove the last command from the redo command stack and return it.
        If the command stack is empty, EmptyCommandStackError is raised.
        """
        try:
            last_redo_command = self.redo_commands.pop()
        except IndexError:
            last_redo_command = None
        return last_redo_command

    def do(self, command, *args, **kwargs):
        """Execute the given command. Exceptions raised from the command are
        not caught."""

        if safe_execute(command.do, *args, **kwargs):
            self.push_undo_command(command)
            self.redo_commands[:] = []  # clear the redo stack when a new command was executed

    def undo(self, n=1):
        """Undo the last n commands. The default is to undo only the last
        command. If there is no command that can be undone because n is too big
        or because no command has been emitted yet, EmptyCommandStackError is
        raised."""

        for _ in range(n):
            command = self.pop_undo_command()
            if command:
                if safe_execute(command.undo):
                    self.push_redo_command(command)

    def redo(self, n=1):
        """Redo the last n commands which have been undone using the undo
        method. The default is to redo only the last command which has been
        undone using the undo method. If there is no command that can be redone
        because n is too big or because no command has been undone yet,
        EmptyCommandStackError is raised."""

        for _ in range(n):
            command = self.pop_redo_command()
            if command:
                if safe_execute(command):
                    self.push_undo_command(command)

    def clear(self, **kwargs):
        for cmd in self.undo_commands:
            cmd.clean(**kwargs)
        self.undo_commands.clear()
        self.redo_commands.clear()
