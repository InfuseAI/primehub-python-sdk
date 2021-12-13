import ast
import os
from unittest import TestCase


class PrintChecker(ast.NodeTransformer):

    def __init__(self, testutil: TestCase, filename: str):
        self.testutil = testutil
        self.filename = filename

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            file_kw_arg = [x for x in node.keywords if x.arg == 'file']
            if len(file_kw_arg) == 0:
                message = f'print should have "file" keyword arg: {self.filename}:{node.lineno}:{node.col_offset}\n'
                message += 'fix it with file=primehub.stderr (it could be primehub.stdout)'
                self.testutil.fail(message)
        return node


def source_contents():
    project_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '../primehub'))
    for root, dirs, files in os.walk(project_dir):
        for f in files:
            if f.endswith('.py'):
                p = os.path.join(root, f)
                with open(p, 'r') as fh:
                    content = fh.read()
                    yield p, content
        break


class PrintTest(TestCase):

    def test_print_with_file_arg(self):
        for filename, c in source_contents():
            node = ast.parse(c)
            PrintChecker(self, filename).visit(node)
