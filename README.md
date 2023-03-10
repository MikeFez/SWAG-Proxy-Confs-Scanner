# SWAG-Proxy-Confs-Scanner
Gather information regarding proxy-confs managed by SWAG.

## What is this?
[SWAG](https://github.com/linuxserver/docker-swag) (Secure Web Application Gateway) sets up a Nginx webserver and reverse proxy with php support and a built-in certbot client that automates free SSL server certificate generation and renewal processes (Let's Encrypt and ZeroSSL). It also contains fail2ban for intrusion prevention.

Basically, SWAG allows you to point requests for specific subdomains to assigned containers, without the need to expose ports.

Subdomain routing is managed via proxy-confs, but there's no simple way to actually grab statistics on the contents. Which ones have authelia enabled? Which ones are only accessible internally?

With _SWAG-Proxy-Confs-Scanner_, now you can know!

## Usage


### docker-compose (recommended, [click here for more info](https://docs.linuxserver.io/general/docker-compose))

```yaml
---
version: "3.9"
services:
  swag: # Configuration options found here: https://docs.linuxserver.io/images/docker-swag
    image: ghcr.io/linuxserver/swag:latest
    container_name: swag
    cap_add:
      - NET_ADMIN
    ports:
      - 80
      - 443
    volumes:
      - ${DOCKER_VOLUMES_DIR}/swag:/config
    environment:
      - PGID
      - PUID
      - TZ
      - EMAIL=${MY_EMAIL}
      - URL=${DOMAIN}
      - SUBDOMAINS
      - VALIDATION=dns
      - DNSPLUGIN=cloudflare
    healthcheck:
      test: "${DOCKER_HEALTHCHECK_TEST:-curl localhost:81}"
      interval: 60s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  swag-proxy-confs-scanner:
    image: ghcr.io/mikefez/swag-proxy-confs-scanner:main
    container_name: swag-proxy-confs-scanner
    ports:
      - 8025
    volumes:
      - ${DOCKER_VOLUMES_DIR}/swag/nginx/proxy-confs:/proxy-confs:ro
    depends_on:
      swag:
        condition: service_healthy
    restart: unless-stopped
```
