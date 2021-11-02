from unittest import TestCase

from primehub import Module


class OutputUtilsTest(TestCase):

    def test_output(self):
        self.assertEqual(['value'], Module.output({'data': {'me': ['value']}}, 'me'))
        self.assertEqual('result', Module.output({'data': {'1': {'2': 'result'}}}, '1.2'))

        # if there is no data, return all payload
        self.assertEqual({'error': ['messages']}, Module.output({'error': ['messages']}, 'any.path.to.data'))
