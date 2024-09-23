import sys
from muscles import ApplicationMeta
from muscles import Context
from ...src.muscles.cli.cli import Console
from ...src.muscles.cli.cli import cli
from ...src.muscles.cli.cli import CliStrategy
from unittest.mock import patch
import io


def test_cli_base_check():
    """
    Проверяем CLI на базовую работу
    :return:
    """

    class TestApp(metaclass=ApplicationMeta):
        context = Context(CliStrategy)

        console = Console()

        def run(self, *args):
            return self.context.execute(*args, shutup=True)

    m = TestApp()

    @cli.group()
    def test_0_0(*args):
        """test_0_0"""
        return 'GroupTest'

    @test_0_0.command(command_name='test_0_1')
    @test_0_0.argument('--arg1', short='-a', required=True, description='Argument 1',
                   prompt='Send Argument 1')
    @test_0_0.argument('--arg2', short='-a2', required=True, flag_value=False, default=100, description='Argument 2',
                   prompt='Send Argument 2')
    @test_0_0.argument('--password', short='-p', required=True, description='Password',
                   prompt='Send Password', hide=True)
    def test_0_1(*args, arg1, arg2, password):
        return arg1, arg2, password

    # result = m.run('test', '-u', 'user', '-p', 'password', '--email', 'email1', 'email2')
    result = m.run('test_0_0')
    assert result == 'GroupTest'

    result = m.run('test_0_0', 'test_0_1', '--arg1', 'val1', '-a2', 'val2', '--password', 'pwd')
    assert result == ('val1', 'val2', 'pwd')

    result = m.run('test_0_0', 'test_0_1', '--arg1', 'val1', '-a2', 'val2', '--password', 'pwd')
    assert result == ('val1', 'val2', 'pwd')


def test_cli_multiple():
    """
    Проверяем CLI на работу атрибута multiple
    :return:
    """

    class TestApp(metaclass=ApplicationMeta):
        context = Context(CliStrategy)

        console = Console()

        def run(self, *args):
            return self.context.execute(*args, shutup=True)

    m = TestApp()

    @cli.group()
    def test_1_0(*args):
        """test_1_0"""
        return 'GroupTest'

    @test_1_0.command(command_name='test_1_1')
    @test_1_0.argument('--arg21', short='-a21', required=True, multiple=True, flag_value=False, default=100,
                         description='Argument 2',
                         prompt='Send Argument 2')
    @test_1_0.argument('--password2', short='-p2', required=True, multiple=True, description='Password',
                         prompt='Send Password', hide=True)
    @test_1_0.argument('--arg20', short='-a20', required=True, multiple=True, description='Argument 1',
                         prompt='Send Argument 1')
    def test_1_1(*args, arg20, arg21, password2):
        return arg20, arg21, password2

    result = m.run('test_1_0')
    assert result == 'GroupTest'

    result = m.run('test_1_0', 'test_1_1', '--arg20', 'val10', 'val11', '--arg21', 'val20', 'val21', 'val22',
                   '--password2', 'pwd1', 'pwd2')
    assert result == (['val10', 'val11'], ['val20', 'val21', 'val22'], ['pwd1', 'pwd2'])

    result = m.run('test_1_0', 'test_1_1', '-a21', 'val10', 'val11', '-a20', 'val20', 'val21', 'val22',
                   '-p2', 'pwd1', 'pwd2')
    assert result == (['val20', 'val21', 'val22'], ['val10', 'val11'], ['pwd1', 'pwd2'])


def test_cli_flag():
    """
    Проверяем CLI на корректность декоратора flag
    :return:
    """

    class TestApp(metaclass=ApplicationMeta):
        context = Context(CliStrategy)

        console = Console()

        def run(self, *args):
            return self.context.execute(*args, shutup=True)

    m = TestApp()

    @cli.command(command_name='test_2_1')
    @cli.flag('--arg21', short='-a21', description='Argument 21')
    @cli.flag('--arg22', short='-a22', description='Argument 22')
    @cli.flag('--arg23', short='-a23', description='Argument 23')
    def test_2_1(*args, arg21, arg22, arg23):
        return arg21, arg22, arg23

    result = m.run('test_2_1', '--arg21', '--arg22', '--arg23')
    assert result == (True, True, True)

    result = m.run('test_2_1', '--arg21', '--arg23')
    assert result == (True, False, True)


def test_cli_prompt(capsys, monkeypatch):
    """
    Проверяем CLI на корректность работы атрибута prompt
    :return:
    """

    class TestApp(metaclass=ApplicationMeta):
        context = Context(CliStrategy)

        console = Console()

        def run(self, *args):
            return self.context.execute(*args, shutup=True)

    m = TestApp()

    @cli.command(command_name='test_3_1')
    @cli.argument('--arg31', short='-a31', description='Argument 31', required=True, prompt="Enter text")
    def test_3_1(*args, arg31):
        return arg31

    def mock_input(prompt):
        assert prompt.strip() == "Enter text"
        return "this is value"

    monkeypatch.setattr('builtins.input', mock_input)

    result = m.run('test_3_1', '--arg21')
    assert result.strip() == "this is value"

    with patch('builtins.input', return_value='this is value 1'):
        result = m.run('test_3_1', '--arg31')
        assert result == "this is value 1"


def test_cli_required():
    """
    Проверяем CLI на корректность работы атрибута required
    :return:
    """

    class TestApp(metaclass=ApplicationMeta):
        context = Context(CliStrategy)

        console = Console()

        def run(self, *args):
            return self.context.execute(*args, shutup=True)

    m = TestApp()

    @cli.command(command_name='test_4_1')
    @cli.argument('--arg41', short='-a41', description='Argument 41', required=True)
    def test_4_1(*args, arg41):
        return arg41

    try:
        result = m.run('test_4_1', '--arg41')
    except ValueError as e:
        assert str(e) == str("Required argument --arg41 is missing")

    result = m.run('test_4_1', '--arg41', 'val41')
    assert str(result) == str("val41")


def test_cli_dest():
    """
    Проверяем CLI
    :return:
    """

    class TestApp(metaclass=ApplicationMeta):
        context = Context(CliStrategy)

        console = Console()

        def run(self, *args):
            return self.context.execute(*args, shutup=True)

    m = TestApp()

    @cli.command(command_name='test_5_1')
    @cli.argument('--arg51', dest='new_args51', short='-a51', description='Argument 51', required=True)
    def test_5_1(*args, new_args51):
        return new_args51

    result = m.run('test_5_1', '--arg51', 'val51')
    assert result == 'val51'


def test_cli_subgroup():
    """
    Проверяем CLI
    :return:
    """

    class TestApp(metaclass=ApplicationMeta):
        context = Context(CliStrategy)

        console = Console()

        def run(self, *args):
            return self.context.execute(*args, shutup=True)

    m = TestApp()

    @cli.group(command_name='test_7_0')
    def test_7_0(*args):
        return 0

    @test_7_0.group(command_name='test_7_1')
    def test_7_1(*args):
        return 1

    @test_7_1.group()
    def test_7_2(*args):
        return 2

    result = m.run('test_7_0')
    assert result == 0

    result = m.run('test_7_0', 'test_7_1')
    assert result == 1

    result = m.run('test_7_0', 'test_7_1', 'test_7_2')
    assert result == 2

    result = m.run('test_7_1')
    assert result == None


def test_cli_help():
    """
    Проверяем CLI возможность вывода
    :return:
    """

    class TestApp(metaclass=ApplicationMeta):
        context = Context(CliStrategy)

        console = Console()

        def run(self, *args):
            return self.context.execute(*args, shutup=False)

    m = TestApp()

    @cli.group()
    def test_6_0(*args):
        """test 6 0"""
        return 'GroupTest'

    @test_6_0.command(command_name='test_6_1')
    @test_6_0.argument('--arg61', dest='new_args61', short='-a61', description='Argument 61', required=True)
    def test_6_1(*args, new_args61):
        return new_args61

    @test_6_0.command(command_name='test_6_2', description="Test 62")
    @test_6_0.argument('--arg62', short='-a62', description='Argument 62')
    @test_6_0.flag('--arg62_2', short='-a62_2', description='Argument 62_2')
    def test_6_2(*args, arg62, arg62_2):
        return arg62, arg62_2

    captured_output = io.StringIO()

    sys.stdout = captured_output
    result = m.run('help')

    sys.stdout = sys.__stdout__

    assert "help - command list" in captured_output.getvalue().strip()
    assert "<command_group> help - help with the command" in captured_output.getvalue().strip()
    assert "test_6_0             - test 6 0" in captured_output.getvalue().strip()
    assert "Muscular" in captured_output.getvalue().strip()
    assert "CLI" in captured_output.getvalue().strip()
    assert "(c) Butko Denis" in captured_output.getvalue().strip()

    captured_output = io.StringIO()

    sys.stdout = captured_output

    result = m.run('test_6_0', 'help')

    sys.stdout = sys.__stdout__

    assert "test_6_0             - test 6 0" in captured_output.getvalue().strip()
    assert "help                 - Command list for test_6_0" in captured_output.getvalue().strip()

    assert "test_6_1             - -" in captured_output.getvalue().strip()
    assert " [--arg61, -a61]     Argument 61" in captured_output.getvalue().strip()
    assert "test_6_2             - Test 62" in captured_output.getvalue().strip()
    assert " --arg62_2, -a62_2   Argument 62_2" in captured_output.getvalue().strip()
    assert " --arg62, -a62       Argument 62" in captured_output.getvalue().strip()
    assert " --arg62, -a62       Argument 63" not in captured_output.getvalue().strip()

