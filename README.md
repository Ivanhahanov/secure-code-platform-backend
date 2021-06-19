### SecureCodePlatform Backend

#### Build
dev:
```bash
docker-compose -f docker-compose-dev.yml up -d
```
В лога create_user сервиса можно будет найти креды к админу и тестовому пользователю
```bash
docker-compose -f docker-compose-dev.yml logs -f create_users
---
create_users_1  | [+] Admin created
create_users_1  | admin:JxvmsiUz
---
create_users_1  | [+] User created
create_users_1  | test:iEznUSuh
---
```
_Пароли будут обновляться каждый раз при перезапуске_

prod:
```bash
docker-compose -f docker-compose-prod.yml up -d
```
View [API](http://localhost)

## TechnicalSupport
`zammad/`

_Note: Zammad UI port conflict with OpenVpn admin port_ 
```
cd zammad
docker-compose up -d
```