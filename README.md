# Cloud Stock
> Сервис синхронизации складских остатков между различными маркетплейсами с возможностью ручного управления

## Get started
Для работы сервиса необходимы `Python >= 3.10` и `Redis`

```bash
git clone git@github.com:BARASHTECH/Cloud-stock.git
cd Cloud-stock
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sh build.sh dev
```

В скрипте сборки аргумент отвечает за способ выключения проекта, в случае `dev` это происходит при `ctrl+c` (SIGINT or INT). При агрументе `deploy` запуск django сервера, celery, redis и serveo (ssh tunnel from localhost) происходит через nohup, скрипт при этом завершается, для выключения проекта в таком случае необходимо выполнить `sh build.sh stop`.

Так же настроена система автоматического применения последних изменений с помощью Github Actions (правда пока без тестов)

## Small docs
По сути сервис состоит из трех компонентов - сайта (Django), базы данных (SQLite) и long polling (celery)

todo
