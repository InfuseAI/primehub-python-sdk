import os.path
from typing import Iterator

from primehub import Helpful, Module, PrimeHubException, cmd


class AdminReport(Helpful, Module):

    @cmd(name='download', description='Download a report by url', optionals=[('dest', str)])
    def download(self, url, **kwargs):
        """
        Download a report csv file from the given url.

        It will convert the URI to filename by default. For example, there are summary url and details url
        * https://primehub-python-sdk.primehub.io/api/report/monthly/2022/12
        * https://primehub-python-sdk.primehub.io/api/report/monthly/details/2022/12

        Will save to
        * 202212.csv
        * 202212_details.csv

        If you give a dest, it will use the given dest as the filename.

        :type url: str
        :param url: The report url.

        :type dest: str
        :param dest: The local path to save the report csv file

        :type recusive: bool
        :param recusive: Copy recursively, it works when a path is a directory.
        """

        def convert_to_filename(url, segment_str, dest):
            if dest:
                return os.path.abspath(dest)
            filename = url.split(segment_str)[1].replace('/', '')
            if 'details' in segment_str:
                return f'{filename}_details.csv'
            return os.path.join(os.getcwd(), f'{filename}.csv')

        dest = kwargs.get('dest')
        filename = None
        if '/monthly/details/' in url:
            filename = convert_to_filename(url, '/monthly/details/', dest)
        elif '/monthly/' in url:
            filename = convert_to_filename(url, '/monthly/', dest)
        else:
            raise PrimeHubException(f'invalid url: {url}')

        def prepare_directory(dest: str):
            try:
                os.truncate(dest, 0)
                return
            except BaseException:
                pass

            try:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
            except BaseException:
                pass

        prepare_directory(filename)
        self.request_file(url, filename)
        return dict(filename=filename)

    @cmd(name='list', description='List reports', optionals=[('page', int)])
    def list(self, **kwargs) -> Iterator:
        """
        List reports

        :type page: int
        :param page: the page of all data

        :rtype Iterator
        :return user iterator
        """

        query = """
        query UsageReportQuery($usageReportPage: Int) {
          usageReport: usageReportsConnection(page: $usageReportPage) {
            edges {
              cursor
              node {
                id
                summaryUrl
                detailedUrl
              }
            }
            pageInfo {
              currentPage
              totalPage
            }
          }
        }
        """

        variables = {'usageReportPage': 1}

        page = kwargs.get('page', 1)
        if page >= 1:
            variables['usageReportPage'] = int(page)
            results = self.request(variables, query)
            if results['data']['usageReport']['edges']:
                for e in results['data']['usageReport']['edges']:
                    yield e['node']
            return

        page = 1
        while True:
            variables['usageReportPage'] = int(page)
            results = self.request(variables, query)
            if results['data']['users']['edges']:
                for e in results['data']['users']['edges']:
                    yield e['node']
                page = page + 1
            else:
                break

    def help_description(self):
        return "Get reports"
