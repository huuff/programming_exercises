import subprocess
import pathlib
import types
from . import command
from . import config
from . import testcase

class BaseTest():
    def __init__(self, root_dir):
        self.root_path = pathlib.Path(root_dir)

    def sanitize_output(self, output):
        if isinstance(output, str):
            return output.rstrip('\n')
        else:
            return output

    def test_template(self):
        self.recursive_descent(self.root_path, config.default())

    def recursive_descent(self, root, config):
        config = config.get_updated(root)
        files = list(root.glob('*'))
        for file in files:
            if file.is_dir():
                print(f"{file.relative_to(self.root_path.parent)}")
                self.recursive_descent(file, config)
            if file == config.get_file(root):
                if config.has_pre():
                    config.get_pre(root).run(config.get_timeout())
                for test_case in self.test_cases():
                    self.run_test(root, config, test_case)
                if config.has_post():
                    config.get_post(root).run(config.get_timeout())

    def run_test(self, directory, config, test_case):
        command = self.configure_command(config.get_run()).set_dir(directory)
        try:
            test_case.run(command, config)
        except subprocess.TimeoutExpired:
            print('Timed out!')

    # def run_test(self, directory, config, test_case, expected):
        # command = self.configure_command(test_case, config.get_run()).set_dir(directory)
        # actual = 'placeholder' # just so the linter doesn't complain
        # try:
            # actual = command.run(config.get_timeout())
            # if isinstance(expected, list): # TODO: this is a hack, must implement test cases to deal with it
                # for i in range(0, len(expected)):
                    # assert expected[i] == self.sanitize_output(actual[i])
            # else:
                # assert expected == self.sanitize_output(actual)
        # except subprocess.TimeoutExpired:
            # print('Timed out!')
        # except AssertionError as error:
            # print(f'Error on input: {test_case}')
            # print(f'Expected: {expected}')
            # if isinstance(expected, list): # TODO: this is a hack, must implement test cases to deal with it
                # print(f'Got: {actual}')
            # else:
                # print(f'Got: {self.sanitize_output(actual)}')
            

    def test_cases(self): # to be implemented in base class
        return {}
    
    def configure_command(self, command): # to be implemented in base class
        return command.Command()
