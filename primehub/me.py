from primehub import Helpful, cmd, Module


class Me(Helpful, Module):

    @cmd(name='me', description='Get user information', return_required=True)
    def me(self) -> dict:
        """
        Get account information

        :rtype: dict
        :returns: account information
        """
        query = """
        query {
          me {
            id
            username
            firstName
            lastName
            email
            isAdmin
          }
        }
        """
        result = self.request({}, query)
        if 'data' in result and 'me' in result['data']:
            return result['data']['me']
        return result

    def help_description(self):
        return "Show user account"
