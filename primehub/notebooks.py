from typing import Iterator

from primehub import Helpful, cmd, Module
import urllib.parse

from primehub.utils.optionals import toggle_flag


class Notebooks(Helpful, Module):
    """
    The notebooks module provides functions to manage Primehub Notebooks
    """

    @cmd(name='logs', description='Get notebooks logs', optionals=[('follow', toggle_flag), ('tail', int)])
    def logs(self, **kwargs) -> Iterator[str]:
        """
        Get notebooks logs

        :type follow: bool
        :param follow: Wait for additional logs to be appended

        :type tail: int
        :param tail: Show last n lines

        :rtype str
        :return The notebooks logs
        """
        follow = kwargs.get('follow', False)
        tail = kwargs.get('tail', 10)

        endpoint = urllib.parse.urljoin(self.endpoint, '/api/logs/jupyterhub')
        return self.primehub.request_logs(endpoint, follow, tail)

    def help_description(self):
        return "Get notebooks logs"
