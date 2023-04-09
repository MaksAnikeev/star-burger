#!/usr/bin/env bash


set -e

echo $(git pull git@github.com:MaksAnikeev/star-burger.git);
echo $(apt-get install python3.10-venv);
echo $(/usr/bin/env python3 -m venv venv);
source "./venv/bin/activate";
echo $(/usr/bin/env pip3 install -r requirements.txt);
npm ci --dev
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
echo $(/usr/bin/env python3 manage.py collectstatic --noinput);
echo $(/usr/bin/env python3 manage.py migrate);

systemctl daemon-reload
systemctl restart postgresql
systemctl restart burger-example
systemctl reload nginx

echo 'Деплой успешно выполнен';