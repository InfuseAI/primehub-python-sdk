import sys

from primehub import Helpful, cmd, has_data_from_stdin, Module
from primehub.utils.permission import ask_for_permission


class DevLab(Helpful, Module):

    @cmd(name='submit-case', description='submit use case')
    def read_from_stdin_or_file(self, *args, **kwargs):
        """
        primehub devlab submit-case abc -f -xd <<EOF
        {
            "instanceType": "cpu-1",
            "image": "base-notebook",
            "displayName": "test",
            "command": "echo \"test1\"\necho \"test2\"",
        }
        EOF

        :param args:
        :param kwargs:
        :return:
        """

        if has_data_from_stdin():
            print("".join(sys.stdin.readlines()))
        print(args, kwargs)

    @cmd(name='cmd', description='show internal commands')
    def print_register_table(self):
        from primehub.utils.decorators import show_debug_info
        show_debug_info()

    @cmd(name='test-query', description='test-graphql')
    def test_query(self):
        query = """
        {
          me {
            effectiveGroups {
              id
              name
              displayName
            }
          }
        }
        """
        results = self.request({}, query)
        return results['data']['me']['effectiveGroups']

    @ask_for_permission
    @cmd(name='say-yes', description='show case for @ask_for_permission')
    def ask_for_permission(self, **kwargs):
        from datetime import datetime
        s = str(datetime.now())
        with open("ask_for_permission.txt", "w") as fh:
            fh.write(s)
            fh.write("\n")
        return dict(message='create a file [ask_for_permission.txt] having the current datetime content')

    def help(self):
        return "help me"

    def help_description(self):
        return "dev-lab is used to the primehub-python-sdk development and testing"
