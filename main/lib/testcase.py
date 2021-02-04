from .command import OneShotCommand, LongRunningCommand
from .logger import *
import subprocess

def sanitize_output(output):
    if isinstance(output, str):
        return output.rstrip('\n')
    else:
        return output

def assert_equals(input, expected, actual, logger):
    try:
        assert expected == actual
    except AssertionError as error:
        logger.log(f'Error on input: {input}', Level.FAIL)
        logger.log(f'Expected: {expected}', Level.FAIL)
        logger.log(f'Got: {actual}', Level.FAIL)

def run_with_timeout(command, config):
    try:
        return command.run(config.get_timeout())
    except (subprocess.TimeoutExpired, TimeoutError):
        return "TIMED OUT"

class TestCase:
    def __init__(self, input, expected):
        self.input = input
        self.expected = expected

class SimpleTestCase(TestCase):
    def __init__(self, input, expected):
        if isinstance(expected, list):
            expected = ' '.join(list(map(str, expected)))
        super().__init__(input, expected)

    def run(self, base_command, root, config):
        command = OneShotCommand(base_command, root, config).add_arg(self.input)
        actual = run_with_timeout(command, config)
        actual = sanitize_output(actual)
        assert_equals(self.input, self.expected, actual, config.get_logger())

class MultiTestCase(TestCase):
    def run(self, base_command, root, config):
        command = OneShotCommand(base_command, root, config)
        actuals = [] 
        for i in range(0, len(self.input)):
            cur_command = command.add_arg(self.input[i])
            actual = run_with_timeout(cur_command, config)
            actual = sanitize_output(actual)
            actuals.append(actual)
        assert_equals(self.input, self.expected, actuals, config.get_logger())

class FuncTestCase(TestCase):
    def run(self, base_command, root, config):
        command = LongRunningCommand(base_command, root, config, self.input)
        actual = run_with_timeout(command, config)
        actual = sanitize_output(actual)
        assert_equals(self.input, self.expected, actual, config.get_logger())
