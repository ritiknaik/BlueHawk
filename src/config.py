import pathlib

abs_path = str(pathlib.Path().absolute().parent)
#Global Configuration

DOCUMENT_ROOT = abs_path

#Default timeout
TIMEOUT = 500

#Default port number
PORT = 8000

#Maximum number of connections supported simulataneously
MAX_CONNECTIONS = 10

#Keep alive timeout
KEEP_ALIVE = 10
