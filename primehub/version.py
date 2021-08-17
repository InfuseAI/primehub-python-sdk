from primehub import Helpful, cmd, Module, __version__


class Version(Helpful, Module):

    @cmd(name='version', description='show version number', return_required=True)
    def version(self) -> str:
        return __version__

    def help_description(self):
        return "Display the version of PrimeHub Python SDK"
