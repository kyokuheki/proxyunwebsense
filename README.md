# proxyunwebsense
The proxyunwebsense is an automated tool on the CLI that clicks the unblock URL of the websense proxy.

## Depends

- requests
- lxml

```shell
pip3 install requests lxml
```

## Run

```shell
python3 proxyunwebsense.py --http_proxy http://127.0.0.1:3128 example.com
# or
export HTTP_PROXY=http://127.0.0.1:3128
export HTTPS_PROXY=http://127.0.0.1:3128
python3 proxyunwebsense.py example.com
```

## Usage
```shell
usage: proxyunwebsence.py [-h] [--http_proxy HTTP_PROXY]
                          [--https_proxy HTTPS_PROXY] [-c COUNT]
                          [url [url ...]]

proxyunwebsence.py: Unblock proxy websence.

positional arguments:
  url

optional arguments:
  -h, --help            show this help message and exit
  --http_proxy HTTP_PROXY
                        HTTP PROXY
  --https_proxy HTTPS_PROXY
                        HTTPS PROXY
  -c COUNT, --count COUNT
                        set the number of unwebsence.
```
