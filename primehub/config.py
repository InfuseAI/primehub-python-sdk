from primehub import Helpful, cmd, Module


# The config module provides functions to update PrimeHub SDK connection and context information
# Config class only changes data in the memory
# CliConfig will change data and update it to the real configuration file.

class Config(Helpful, Module):

    def set_endpoint(self, endpoint: str):
        self.primehub.primehub_config['endpoint'] = endpoint

    def set_token(self, token: str):
        self.primehub.primehub_config['token'] = token

    def set_group(self, group: str):
        self.primehub.primehub_config['group'] = group

    def help_description(self):
        return "Update the settings of PrimeHub SDK"


class CliConfig(Config):

    @cmd(name='set-endpoint', description='set endpoint and save to the config file')
    def set_endpoint(self, endpoint: str):
        super(CliConfig, self).set_endpoint(endpoint)
        self.update()

    @cmd(name='set-token', description='set token and save to the config file')
    def set_token(self, token: str):
        super(CliConfig, self).set_token(token)
        self.update()

    @cmd(name='set-group', description='set group and save to the config file')
    def set_group(self, group: str):
        super(CliConfig, self).set_group(group)
        self.update()

    def update(self):
        self.primehub.primehub_config.save()
