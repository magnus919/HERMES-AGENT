---
name: deploy-php-mariadb-apache-app
description: Deploy a plain PHP + MariaDB application from GitHub onto Ubuntu using Apache, import a bundled SQL dump, wire DB credentials through Apache SetEnv, and verify the site end-to-end.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Deploy, PHP, MariaDB, Apache, Ubuntu, SQL, VirtualHost]
---

# Deploy PHP + MariaDB + Apache App

Use this skill when a repo is a plain PHP app (no Composer/Laravel framework required), contains a SQL dump, and should be deployed on Ubuntu behind Apache.

## When this applies

Typical signals:
- repo contains many `.php` files and static `.html` pages
- database config uses `getenv('DB_HOST')`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- repo ships with a `.sql` dump such as `peminjaman.sql`
- root contains `.htaccess`, suggesting Apache is the simplest web server choice

## Steps

1. Inspect the repo
- find the SQL dump
- inspect database config file
- inspect `.htaccess`
- identify any writable directories (uploads, queue folders, cache folders)

2. Install server packages on Ubuntu

```bash
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  apache2 mariadb-server libapache2-mod-php php php-mysql php-curl php-mbstring php-xml
```

3. Deploy repo to a stable document-root path

Example:

```bash
sudo mkdir -p /var/www/example.com
sudo git clone https://github.com/OWNER/REPO.git /var/www/example.com/current
```

If it already exists:

```bash
sudo git -C /var/www/example.com/current pull --ff-only
```

4. Create DB and import SQL
- generate an app password
- create DB and app user
- import the SQL dump into the target DB

Example:

```bash
DB_PASS=$(openssl rand -base64 24 | tr -dc 'A-Za-z0-9' | head -c 32)
sudo systemctl enable --now mariadb
sudo mariadb <<SQL
DROP DATABASE IF EXISTS appdb;
CREATE DATABASE appdb CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
DROP USER IF EXISTS 'appuser'@'localhost';
CREATE USER 'appuser'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON appdb.* TO 'appuser'@'localhost';
FLUSH PRIVILEGES;
SQL
sudo mariadb appdb < /var/www/example.com/current/app.sql
```

5. Prepare writable directories
Set practical permissions for directories written by PHP.
A good default is owner `ubuntu`, group `www-data`, normal files 644, dirs 755, writable dirs 775.

6. Configure Apache virtual host
Because plain PHP apps often use `getenv()`, prefer Apache `SetEnv` rather than hardcoding secrets into repo files.

Example vhost:

```apache
<VirtualHost *:80>
    ServerName example.com
    ServerAlias www.example.com
    DocumentRoot /var/www/example.com/current

    <Directory /var/www/example.com/current>
        AllowOverride All
        Require all granted
        Options FollowSymLinks
        DirectoryIndex index.html index.php
    </Directory>

    SetEnv DB_HOST localhost
    SetEnv DB_NAME appdb
    SetEnv DB_USER appuser
    SetEnv DB_PASSWORD SECRET

    ErrorLog ${APACHE_LOG_DIR}/example-error.log
    CustomLog ${APACHE_LOG_DIR}/example-access.log combined
</VirtualHost>
```

Then:

```bash
sudo a2enmod rewrite headers
sudo a2ensite example.com.conf
sudo a2dissite 000-default.conf || true
sudo apache2ctl configtest
sudo systemctl enable --now apache2
sudo systemctl reload apache2
```

## Verification checklist

1. Services:

```bash
systemctl is-active apache2
systemctl is-active mariadb
```

2. App page via origin host header:

```bash
curl -I http://127.0.0.1/ -H 'Host: example.com'
```

3. App page via real domain:

```bash
curl -I http://example.com/
```

4. DB user can query target DB:

```bash
mariadb -u appuser -p'PASSWORD' -D appdb -Nse 'SELECT COUNT(*) FROM users;'
```

5. App login or a representative API works end-to-end.
Use a known seeded credential from the imported SQL when possible.

## Pitfalls

- If the repo ships `.htaccess`, remember `AllowOverride All` and enable `rewrite`.
- If the domain sits behind Cloudflare, external DNS may resolve to Cloudflare IPs instead of the VPS IP directly. That is fine as long as the origin still serves the site correctly.
- Avoid committing timestamp-only report churn in backup repos.
- If you store DB credentials in Apache `SetEnv`, back up the vhost config as part of migration state.
