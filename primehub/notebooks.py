from typing import Iterator

from primehub import Helpful, cmd, Module
import urllib.parse


class Notebooks(Helpful, Module):

    @cmd(name='logs', description='Get notebooks logs', optionals=[('follow', bool), ('tail', int)])
    def logs(self, **kwargs) -> Iterator[str]:
        follow = kwargs.get('follow', False)
        tail = kwargs.get('tail', 10)

        endpoint = urllib.parse.urljoin(self.endpoint, '/api/logs/jupyterhub')
        return self.primehub.request_logs(endpoint, follow, tail)

    def help_description(self):
        return "Get notebooks logs"
