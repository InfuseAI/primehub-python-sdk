import json
import time
from tempfile import mkstemp

from primehub import Helpful, cmd, Module
from primehub.config import Config
from primehub.groups import Groups
from primehub.utils import create_logger

logger = create_logger('e2e')


class E2EForBasicFunction(Helpful, Module):

    def title(self, name):
        print("{} {:15s} {}".format('=' * 30, name, '=' * 30))

    def endline(self):
        print()
        print()

    @cmd(name='basic-functions', description='run basic functions')
    def basic_functions(self):
        self.title('Config')
        c: Config = self.primehub.config
        c.primehub.primehub_config.save(path='./e2e-config.json')
        print('save config to ', './e2e-config.json')
        self.endline()

        self.title('Info')
        print(self.primehub.info.info())
        self.endline()

        self.title('Groups')
        group: Groups = self.primehub.groups
        for g in group.list():
            print(g['id'], g['name'])
        self.endline()

        self.title('Jobs')
        self.job_e2e()

    def job_e2e(self):
        instance_types = [x for x in self.primehub.instancetypes.list() if "gpu" not in x]
        instance_type = None
        for x in instance_types:
            if 'cpu-half' in x['name']:
                instance_type = x['id']
                break
            if 'cpu-1' in x['name']:
                instance_type = x['id']
                break
        print('instance-type:', instance_type)
        scripts = r"""
        sudo apt-get update -y
        sudo apt-get install -y git
        pip install git+https://github.com/InfuseAI/primehub-python-sdk.git@main
        primehub -h
        echo
        exit 0
        """
        job_spec = dict(instanceType=instance_type, image="base-notebook", displayName="job-e2e", command=scripts)
        fd, path = mkstemp(".json")
        with open(path, "w") as fh:
            fh.write(json.dumps(job_spec))

        my_job = self.primehub.jobs._submit_cmd(file=path)
        my_id = my_job['id']
        print("Job ID:", my_job['id'])

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

            if last_state == 'Cancelled':
                break
            time.sleep(1)

        print("Logs:")
        for g in self.primehub.jobs.logs(my_id, follow=True):
            print(g)

    def help_description(self):
        return "dev-lab is used to the primehub-python-sdk development and testing"
