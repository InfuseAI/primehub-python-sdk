from typing import Iterator

from primehub import Helpful, cmd, Module


class Models(Helpful, Module):

    @cmd(name='list', description='List PrimeHub Applications', return_required=True)
    def list(self) -> Iterator:
        """
        List models

        :rtype: Iterator
        :returns: All registered models
        """
        return []

    def help_description(self):
        return "Manage models"
