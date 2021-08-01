import os
import json
from typing import Iterator

import requests  # type: ignore
from urllib3.exceptions import NewConnectionError

from primehub.utils import create_logger

logger = create_logger('primehub-http')


class GraphQLException(BaseException):
    pass


class Client(object):

    def __init__(self, primehub_config):
        self.primehub_config = primehub_config

    def request(self, variables: dict, query: str):
        request_body = dict(variables=json.dumps(variables), query=query)
        headers = {'authorization': 'Bearer {}'.format(self.primehub_config.api_token)}
        try:
            content = requests.post(self.primehub_config.endpoint, data=request_body, headers=headers).text
        except NewConnectionError as e:
            logger.exception(exc_info=e)
            return GraphQLException(e)
        result = json.loads(content)
        if 'errors' in result:
            raise GraphQLException(result)
        return result

    def request_logs(self, endpoint, follow, tail) -> Iterator[str]:
        params = {'follow': 'false'}
        if follow:
            params['follow'] = 'true'
        if tail:
            params['tailLines'] = str(tail)
        headers = {'authorization': 'Bearer {}'.format(self.primehub_config.api_token)}

        with requests.get(endpoint, headers=headers, params=params, stream=follow) as response:
            if follow:
                for line in response.iter_lines():
                    yield line.decode()
            else:
                yield response.text

    def request_file(self, endpoint, dest):
        headers = {'authorization': 'Bearer {}'.format(self.primehub_config.api_token)}
        with requests.get(endpoint, headers=headers) as r:
            dir = os.path.dirname(dest)
            if not os.path.isdir(dir):
                os.makedirs(dir)
            with open(dest, 'wb') as f:
                f.write(r.content)
        return


if __name__ == '__main__':
    print(Client.__module__)
