#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
fi

export CELERY_LOG="$LOG_DIR/celery.log"

create_logs() {
    rm "$LOG_DIR/celery.log"
    rm "$LOG_DIR/gunicorn-access.log"
    rm "$LOG_DIR/gunicorn-error.log"
    touch "$CELERY_LOG"
    echo "Created $CELERY_LOG"
}

# for stop dev mode
cleanup() {
    python manage.py close_connections
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
    python manage.py close_connections
    systemctl stop celery_worker.service
    systemctl stop celery_beat.service
    echo "Celery stopped"
    systemctl stop gunicorn.service
    echo "Gunicorn stopped"
    systemctl stop nginx
    echo "Nginx stopped"

elif [[ "$mode" == "dev" ]]; then
    rm -rf Cloud_Stock/migrations/ && rm db/db.sqlite3
    # python manage.py collectstatic --noinput
    python manage.py makemigrations Cloud_Stock
    python manage.py migrate
    python manage.py create_users
    python manage.py preload "config/Cloud Stock - preload_data - Артикулы.csv"
    python manage.py load_stocks
    redis-server &
    python manage.py prefill_cache
    python manage.py runserver &
    celery -A Cloud_Stock worker --loglevel=warning &
    celery -A Cloud_Stock beat --loglevel=warning &

    wait

elif [[ "$mode" == "deploy" ]]; then
    sudo systemctl stop clhb.service celery_beat.service celery_worker.service gunicorn.service nginx redis 

    cd /home/dev/Cloud-Stock
    source /home/dev/Cloud-Stock/venv/bin/activate
    pip install -r requirements.txt
    create_logs
    
    rm -rf Cloud_Stock/migrations/ && rm db/db.sqlite3

    python manage.py close_connections
    python manage.py collectstatic --noinput
    python manage.py makemigrations Cloud_Stock
    python manage.py migrate
    python manage.py create_users
    python manage.py preload "config/Cloud Stock - preload_data - Артикулы.csv"
    python manage.py load_stocks
    sudo systemctl start redis
    python manage.py prefill_cache
    sudo systemctl link /home/dev/Cloud-total_stock-health-bot/clhb.service
    sudo systemctl link /home/dev/Cloud-Stock/systemd_services/celery_worker.service
    sudo systemctl link /home/dev/Cloud-Stock/systemd_services/celery_beat.service
    sudo systemctl link /home/dev/Cloud-Stock/systemd_services/gunicorn.service
    sudo ln -sf /home/dev/Cloud-Stock/systemd_services/cs_nginx_conf /etc/nginx/sites-available/
    sudo ln -sf /etc/nginx/sites-available/cs_nginx_conf /etc/nginx/sites-enabled/
    sudo systemctl daemon-reload
    sudo systemctl start gunicorn gunicorn.socket celery_worker.service celery_beat.service nginx clhb.service

else
    echo "Invalid argument: $mode. Use 'dev' or 'deploy'."
    exit 1
fi
