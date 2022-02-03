<p align="center">
 <img width=250px height=250px src="resources/logos/BlueHawk logo.png" alt="Server logo"></a>
</p>

<h2 align="center">BlueHawk 1.0 HTTP Server</h3>

---

<p align="center"> BlueHawk is an HTTP/1.1 compliant web server.
    <br> 
</p>

## 📝 Table of Contents

- [About](#about)
- [Usage](#usage)
- [Testing](#testing)
- [Acknowledgments](#acknowledgements)

## About <a name = "about"></a>

This project is done as a part of Computer Networks course. It aims at the implementation of the HTTP/1.1 Protocol based on RFC 2616 and includes the basic HTTP methods of `GET`, `POST`, `PUT`, `DELETE` and `HEAD`.

### Prerequisites

1. Python 3.x

For installing necessary dependencies run the following command:

```sh
$ pip3 install -r dependencies.txt
```

## Usage <a name = "usage"></a>

Follow the given steps to run the server

```sh
$ cd src
$ bash bluehawk.sh
```

This will run the server on a default port defined in the config.py file. You can customize the configuration by editing the config file in the src/ directory. Options available in the config file are:

```
1. DOCUMENT_ROOT : The document root directory of the server that will serve the requests
2. TIMEOUT : The Timeout value for the response
3. PORT : The port on which the server will listen
4. MAX_CONNECTIONS : The maximum number of parallel connections that the server should serve
5. KEEP_ALIVE : Time for which a connection is to be kept alive
```

To stop the server press `Ctrl-C`

To get more information about the server, run the `bluehawk.sh` file with `-i` option

```sh
$ cd src
$ bash bluehawk.sh -i
```

## Testing the server <a name = "testing"></a>

A script file `test.sh` will perform automated testing of the server for all implemented methods and status codes along with multithreading.
It will save the expected response along with received response in `results.txt` file. You can browse through the file to understand the differences if there are any.

For testing, run the following command in a new terminal window (Note: Make sure that the server is up and running in another window)

```sh
$ bash test.sh
```

It will take a minute to complete all the tests
(Note: Some test cases might fail because of `If-Match` and `If-Modified` headers as those values are changed when you clone the repo)

##### You can also add your own test cases in the request.txt file and expected correct response in the testing.py file

## Acknowledgements <a name = "acknowledgements"></a>

- [RFC2616](https://datatracker.ietf.org/doc/html/rfc2616)
- [MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP)
