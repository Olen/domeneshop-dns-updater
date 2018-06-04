# domeneshop-dns-updater

As domeneshop is missing an API, this small util provides an automated way to update the _acme-challenge TXT record needed for certbot automatic renewals


# 1. Run from host

## Install
```sh
pip install -r requirements.txt
```

## Configure
```sh
cp config.yml-default config.yml
```

Add username and password, id for domain (7 digits) and the domains to update.

## Run

```sh
certbot certonly --manual --manual-auth-hook domeneshop.py --agree-tos --manual-public-ip-logging-ok -d <domain.name>

```

## Certbot-config
Make sure your renewal-config contains the following:
### /etc/letsencrypt/renewal/domain.name.conf
```
pref_challs = dns-01,
server = https://acme-v02.api.letsencrypt.org/directory
authenticator = manual
installer = None
manual_public_ip_logging_ok = True
manual_auth_hook = /path/to/domeneshop-dns-updater/domeneshop.py

```


# Credit

Forked from https://github.com/runelangseid/domeneshop-dns-updater
