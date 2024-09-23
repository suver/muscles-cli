from __future__ import annotations
from .command import Group, Command

import os


class Console:
    """
    Главный инстанс для подключения консольных команды
    Так же создает базовую консольную группу cli

    """

    try:
        rows, columns = os.popen('stty size', 'r').read().split()
    except BaseException as e:
        rows = 50
        columns = 100

    def __init__(self):
        self.root_group = Group(['cli'])
        self.root_group.command_name = 'cli'
        self.root_group.handler = self.handler
        self.root_group.description = ''
        self.root_group.function_name = 'console.handler'

        command = Command(['help'] + self.root_group.key)
        command.function_name = self.root_group.help.__name__
        command.handler = self.root_group.help
        command.command_name = 'help'
        command.description = "Command List"

        self.root_group.add(command)

    def __call__(self, *args, **kwargs):
        return self.root_group

    def handler(self, *args, **kwargs):
        pass


console = Console()


cli = console.root_group

