import json

import requests  # type: ignore


class GraphQLException(BaseException):
    pass


class Client(object):

    def __init__(self, primehub_config):
        self.primehub_config = primehub_config

    def request(self, variables: dict, query: str):
        request_body = dict(variables=json.dumps(variables), query=query)
        headers = {'authorization': 'Bearer {}'.format(self.primehub_config.api_token)}
        content = requests.post(self.primehub_config.endpoint, data=request_body, headers=headers).text
        result = json.loads(content)
        if 'errors' in result:
            raise GraphQLException(result)
        return result

    def request_logs(self, endpoint, follow, tail):
        params = {'follow': 'false'}
        if follow:
            params['follow'] = 'true'
        if tail:
            params['tailLines'] = str(tail)
        headers = {'authorization': 'Bearer {}'.format(self.primehub_config.api_token)}
        content = requests.get(endpoint, headers=headers, params=params, stream=follow)
        return content


if __name__ == '__main__':
    print(Client.__module__)
