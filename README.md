# OpenSSL

https://gist.github.com/marshalhayes/ca9508f97d673b6fb73ba64a67b76ce8

```shell
cd .ssh

openssl genrsa -out rootCA.key 2048
openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 365 -out rootCA.pem
```
