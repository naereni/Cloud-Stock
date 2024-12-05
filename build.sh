#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
fi

export CELERY_LOG="$LOG_DIR/celery.log"

create_logs() {
    rm "$LOG_DIR/*"
    touch "$CELERY_LOG"
    echo "Created $CELERY_LOG"
}

# for stop dev mode
cleanup() {
    kill -9 $(pgrep -f "celery") 1> /dev/null 2> /dev/null
    echo "Celery stopped"
    kill -9 $(pgrep -f "runserver") 1> /dev/null 2> /dev/null
    echo "Django stopped"
    redis-cli shutdown
    rm $SCRIPT_DIR/dump.rdb
    rm -rf Cloud_Stock/migrations/ && rm db/db.sqlite3
    rm celerybeat-schedule
}

os_name=$(uname)

if [[ "$os_name" == "Linux" ]]; then
    if grep -i Ubuntu /etc/os-release >/dev/null 2>&1; then
        trap cleanup INT
    else
        trap cleanup SIGINT
    fi
elif [[ "$os_name" == "Darwin" ]]; then
    # macOS
    trap cleanup SIGINT
else
    trap cleanup SIGINT
fi

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 {dev|deploy|stop}"
    exit 1
fi

mode="$1"

if [[ "$mode" == "stop" ]]; then
    systemctl stop celery_worker.service
    systemctl stop celery_beat.service
    echo "Celery stopped"
    systemctl stop gunicorn.service
    echo "Gunicorn stopped"
    systemctl stop nginx
    echo "Nginx stopped"

elif [[ "$mode" == "dev" ]]; then
    rm -rf Cloud_Stock/migrations/ && rm db/db.sqlite3
    python manage.py makemigrations Cloud_Stock
    python manage.py migrate
    python manage.py create_users
    python manage.py preload "config/Cloud Stock - preload_data - Артикулы.csv"
    python manage.py load_stocks
    redis-server &
    python manage.py runserver &
    celery -A Cloud_Stock worker -l INFO &
    celery -A Cloud_Stock beat --loglevel=info &

    wait

elif [[ "$mode" == "deploy" ]]; then
    source venv/bin/activate
    pip install -r requirements.txt
    create_logs
    rm -rf Cloud_Stock/migrations/ && rm db/db.sqlite3
    python manage.py makemigrations Cloud_Stock
    python manage.py migrate
    python manage.py create_users
    python manage.py preload "config/Cloud Stock - preload_data - Артикулы.csv"
    python manage.py load_stocks

    sudo systemctl stop celery_beat.service celery_worker.service gunicorn.service nginx redis
    sudo ln -sf /home/dev/Cloud-stock/systemd_services/celery_worker.service /etc/systemd/system/
    sudo ln -sf /home/dev/Cloud-stock/systemd_services/celery_beat.service /etc/systemd/system/
    sudo ln -sf /home/dev/Cloud-stock/systemd_services/gunicorn.service /etc/systemd/system/
    sudo ln -sf /home/dev/Cloud-stock/nginx/cs_nginx_conf /etc/nginx/sites-available/
    sudo ln -sf /etc/nginx/sites-available/cs_nginx_conf /etc/nginx/sites-enabled/
    sudo systemctl daemon-reload
    sudo systemctl start redis gunicorn celery_worker.service celery_beat.service nginx

else
    echo "Invalid argument: $mode. Use 'dev' or 'deploy'."
    exit 1
fi
