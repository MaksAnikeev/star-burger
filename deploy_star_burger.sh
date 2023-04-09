#!/usr/bin/env bash


set -e

echo $(git pull git@github.com:MaksAnikeev/star-burger.git);
echo $(apt-get install python3.10-venv);
echo 'Создвем папку виртуального окружения venv';
echo $(/usr/bin/env python3 -m venv venv);
echo 'Активируем текущее виртуальное окружение';
source "./venv/bin/activate";
echo 'Устанавливаем зависимости из requirements.txt';
echo $(/usr/bin/env pip3 install -r requirements.txt);
echo 'Устанавливаем библиотеки Node.js';
npm ci --dev
echo 'Пересобираем js код';
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
echo 'Напишите yes если необходимо перезаписать имеющиеся файлы статики, или no усли нет. И нажмите enter';
echo $(/usr/bin/env python3 manage.py collectstatic --noinput);
echo $(/usr/bin/env python3 manage.py migrate);

systemctl daemon-reload
systemctl restart postgresql
systemctl restart burger-example
systemctl reload nginx