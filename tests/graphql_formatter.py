import subprocess
import tempfile


def is_formatter_available():
    try:
        process = subprocess.run(['prettier', '-h'], capture_output=True)
        return process.stdout.decode('utf8').startswith('Usage: prettier')
    except BaseException:
        return False


def format_graphql(graphql_query):
    _, gql = tempfile.mkstemp(suffix=".graphql")
    with open(gql, 'w') as f:
        f.write(graphql_query)
    process = subprocess.run(['prettier', gql], capture_output=True)
    if process.returncode != 0:
        raise BaseException(f'Can not format the query:\n\n{graphql_query}\n')
    return process.stdout.decode('utf8')
