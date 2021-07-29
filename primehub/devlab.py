import json
import sys
import time
from tempfile import mkstemp

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

    @cmd(name='regression-job-logs', description='regression')
    def regression(self):
        instance_type = [x for x in self.primehub.instancetypes.list() if "gpu" not in x][0]['id']
        scripts = r'bash -c "for i in {1..5}; do date; sleep 1; done"'
        job_spec = dict(instanceType=instance_type, image="base-notebook", displayName="test-from-cli", command=scripts)
        fd, path = mkstemp(".json")
        with open(path, "w") as fh:
            fh.write(json.dumps(job_spec))

        my_job = self.primehub.jobs.submit(file=path)
        my_id = my_job['id']
        print("job id:", my_job['id'])

        last_state = None
        while True:
            p = self.primehub.jobs.get(my_id)['phase']
            if last_state is None:
                last_state = p

            if p != last_state:
                print("Job Phase: {} -> {}".format(last_state, p))
                last_state = p

            if last_state == 'Running':
                break

            if last_state == 'Succeeded':
                break
            time.sleep(1)

        print("Logs:")
        for g in self.primehub.jobs.logs(my_id, follow=True):
            print(g)

    def help_description(self):
        return "dev-lab is used to the primehub-python-sdk development and testing"
