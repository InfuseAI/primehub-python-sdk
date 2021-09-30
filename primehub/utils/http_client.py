import json
from json import JSONDecodeError
from typing import Iterator, Callable

import requests  # type: ignore

from primehub.utils import ResponseException, RequestException, GraphQLException, create_logger, \
    ResourceNotFoundException

logger = create_logger('http')


class Client(object):

    def __init__(self, primehub_config):
        self.primehub_config = primehub_config
        self.timeout = 10

    def request(self, variables: dict, query: str, error_handler: Callable = None):
        request_body = dict(variables=json.dumps(variables), query=query)
        logger.debug('request body: {}'.format(request_body))
        headers = {'authorization': 'Bearer {}'.format(self.primehub_config.api_token)}
        try:
            content = requests.post(self.primehub_config.endpoint, data=request_body, headers=headers,
                                    timeout=self.timeout).text
            logger.debug('response: {}'.format(content))
            result = json.loads(content)
            if 'errors' in result:
                if error_handler:
                    error_handler(result)
                raise GraphQLException(result)
            return result
        except JSONDecodeError:
            raise ResponseException("Response is not valid JSON:\n{}".format(content))
        except ResourceNotFoundException as e:
            raise e
        except BaseException as e:
            raise RequestException(e)

    def request_logs(self, endpoint, follow, tail) -> Iterator[bytes]:
        params = {'follow': 'false'}
        if follow:
            params['follow'] = 'true'
        if tail:
            params['tailLines'] = str(tail)
        headers = {'authorization': 'Bearer {}'.format(self.primehub_config.api_token)}

        with requests.get(endpoint, headers=headers, params=params, stream=follow) as response:
            for chunk in response.iter_content(chunk_size=8192):
                yield chunk

    def request_file(self, endpoint, dest):
        headers = {'authorization': 'Bearer {}'.format(self.primehub_config.api_token)}
        with requests.get(endpoint, headers=headers) as r:
            with open(dest, 'wb') as f:
                f.write(r.content)
        return


if __name__ == '__main__':
    print(Client.__module__)
