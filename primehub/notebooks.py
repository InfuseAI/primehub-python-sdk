from primehub import Helpful, cmd, Module
import urllib.parse


class Notebooks(Helpful, Module):

    @cmd(name='logs', description='Get notebooks logs', optionals=[('follow', bool), ('tail', int)])
    def logs(self, **kwargs):
        follow = kwargs.get('follow', False)
        tail = kwargs.get('tail', 10)

        endpoint = urllib.parse.urljoin(self.primehub_config.endpoint, '/api/logs/jupyterhub')
        response = self.request_logs(endpoint, follow, tail)
        if follow:
            try:
                for s in response.iter_lines():
                    print(s.decode())
            finally:
                response.close()
                return
        return response.text

    def help_description(self):
        return "Get notebooks logs"
