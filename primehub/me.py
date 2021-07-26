from primehub import Helpful, cmd, Module


class Me(Helpful, Module):

    @cmd(name='me', description='Let me tell you who you are!')
    def me(self):
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
        return "Get user data"
