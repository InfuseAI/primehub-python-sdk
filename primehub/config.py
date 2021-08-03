from primehub.utils import create_logger, group_not_found, RequestException

from primehub import Helpful, cmd, Module

logger = create_logger('cmd-config')


class Config(Helpful, Module):
    """
    The config module provides functions to update PrimeHubConfig.

    Config class only changes data in the memory,
    otherwise CliConfig will change data and update it to the real configuration file.

    In SDK mode, config will use Config.
    In Command mode, config will use CliConfig.
    CliConfig will update the file config after a `set_*` method call.
    """

    def set_endpoint(self, endpoint: str):
        """
        Set endpoint to the GraphQL API.

        It usually is in this pattern https://<primehub-domain>/api/graphql

        :type endpoint: str
        :param endpoint: an URL to GraphQL API endpoint
        """
        self.primehub.primehub_config.endpoint = endpoint

    def set_token(self, token: str):
        """
        Set api-token to the PrimeHubConfig

        :type token: str
        :param token: a token used by GraphQL request
        """
        self.primehub.primehub_config.api_token = token

    def set_group(self, group: str):
        """
        Set current group to work with group aware actions.

        When setting a group, it will validate the group. It the group is invalid, PrimeHub.current_group will be None.

        :type group: str
        :param group: group name
        """
        self.primehub.primehub_config.group = group
        try:
            selected_group = self._fetch_group_info(group)
            if selected_group is None:
                logger.info('Cannot find the group [%s] in the effective groups', group)
            else:
                self.primehub.primehub_config.current_group = selected_group
        except BaseException as e:
            logger.exception('Cannot fetch group [%s] from api-server', group, exc_info=e)
            pass

    def _fetch_group_info(self, group):
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
        try:
            results = self.request({}, query)
            for g in results['data']['me']['effectiveGroups']:
                if g['name'] == group:
                    return g
        except RequestException as e:
            logger.warning(e)
            pass

    def help_description(self):
        return "Update the settings of PrimeHub SDK"


class CliConfig(Config):

    @cmd(name='set-endpoint', description='set endpoint and save to the config file')
    def set_endpoint(self, endpoint: str):
        """
        Set endpoint to the GraphQL API.

        It usually is in this pattern https://<primehub-domain>/api/graphql

        :type endpoint: str
        :param endpoint: an URL to GraphQL API endpoint
        """
        super(CliConfig, self).set_endpoint(endpoint)
        self.update()

    @cmd(name='set-token', description='set token and save to the config file')
    def set_token(self, token: str):
        """
        Set api-token to the PrimeHubConfig

        :type token: str
        :param token: a token used by GraphQL request
        """
        super(CliConfig, self).set_token(token)
        self.update()

    @cmd(name='set-group', description='set group and save to the config file')
    def set_group(self, group: str):
        """
        Set current group to work with group aware actions.

        When setting a group, it will validate the group. It the group is invalid, PrimeHub.current_group will be None.

        :type group: str
        :param group: group name
        """
        super(CliConfig, self).set_group(group)
        if not self.primehub.primehub_config.group_info:
            group_not_found(group)
        if not self.primehub.primehub_config.group_info.get('id', None):
            group_not_found(group)
        self.update()

    def update(self):
        self.primehub.primehub_config.save()
