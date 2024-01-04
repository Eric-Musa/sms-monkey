# sms-monkey
Dockerized Twilio application to be hosted in my AWS Lightsail instance - Github repo to help streamline local vs remote development.


### HOW TO RUN THIS APP BESIDE WORDPRESS

1. Added:
```
# API Proxy
ProxyPass /api/ http://127.0.0.1:5000/api/
ProxyPassReverse /api/ http://127.0.0.1:5000/api/
```
to the top of `/home/bitnami/stack/apache/conf/vhosts/wordpress-https-vhost.conf`:
```
<VirtualHost 127.0.0.1:443 _default_:443>
  ServerName www.example.com
  ServerAlias *
  SSLEngine on
  SSLCertificateFile "/opt/bitnami/apache/conf/ericmusa.com.crt"
  SSLCertificateKeyFile "/opt/bitnami/apache/conf/ericmusa.com.key"
  DocumentRoot /opt/bitnami/wordpress
  # BEGIN: Configuration for letsencrypt
  Include "/opt/bitnami/apps/letsencrypt/conf/httpd-prefix.conf"
  # END: Configuration for letsencrypt
  # BEGIN: Support domain renewal when using mod_proxy without Location
  <IfModule mod_proxy.c>
    ProxyPass /.well-known !
  </IfModule>
  # END: Support domain renewal when using mod_proxy without Location

  # API Proxy
  ProxyPass /api http://127.0.0.1:5000/api
  ProxyPassReverse /api http://127.0.0.1:5000/api
  ...

```

2. Running `Flask` app inside Lightsail instance
```
from flask import Flask

app = Flask(__name__)

@app.route("/api")
def hello_world():
    return "<p>Hello, ERM's Phone!</p>"
```
   
accessible inside the instance by `flask run` and then `curl 127.0.0.1:5000/api`

3. restart Apache
`sudo /opt/bitnami/ctlscript.sh restart apache`


4. package and run the `Flask` app as a container and run headlessly on the Lightsail instance

### CONTAINERIZATION:
- https://docs.docker.com/engine/install/ubuntu/
- instead of `https://download.docker.com/linux/ubuntu`, Lightsail apparently uses Debian, so `https://download.docker.com/linux/debian`

`docker build -t sms-monkey-flask .`
`docker run -p 5000:5000 sms-monkey-flask`

- wrote `run_docker` with ChatGPT to run/restart the container as needed
`sudo run_docker` runs the container if it is not already running
`sudo run_docker -r` stops any running container and starts a new one
`sudo run_docker -b` or `sudo run_docker -rb` rebuild and rerun the image 


5. Added new ProxyPass for my LLaMa2 models:
  # API Proxy
```
  <IfModule mod_proxy.c>
    ProxyPass /.well-known !
  </IfModule>
  # END: Support domain renewal when using mod_proxy without Location

  # API Proxy
  ProxyPass /sms-monkey http://127.0.0.1:5000/sms-monkey
  ProxyPassReverse /sms-monkey http://127.0.0.1:5000/sms-monkey

  # ProxyPass /chat/completions http://127.0.0.1:10001/chat/completions
  # ProxyPassReverse /chat/completions http://127.0.0.1:10001/chat/completions
  # ProxyPass /completions http://127.0.0.1:10001/completions
  # ProxyPassReverse /completions http://127.0.0.1:10001/completions

  # BEGIN: Enable non-www to www redirection
```