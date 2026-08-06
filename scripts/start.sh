#!/bin/bash
cd /home/yang/frappe-bench

export PATH=/home/yang/.local/bin:/home/yang/.nvm/versions/node/v24/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export NVM_DIR=/home/yang/.nvm
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

sudo fuser -k 11000/tcp 13000/tcp 8000/tcp 2>/dev/null
sudo service mariadb start 2>/dev/null
sudo service redis-server start 2>/dev/null

grep -v "^schedule:" Procfile > Procfile.dev

echo ""
echo "启动成功！浏览器打开 http://dev.localhost:8000"
echo "按 Ctrl+C 停止服务器"
echo ""

HONCHO_PROCFILE=Procfile.dev bench start
