#!/bin/bash
# =============================================================================
# ERPNext 开发环境快速启动脚本
# 用法：bash start-dev.sh
# =============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BENCH_DIR="$HOME/frappe-bench"
SITE="dev.localhost"

info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()   { echo -e "${RED}[ERROR]${NC} $1"; }

echo -e "${GREEN}"
echo "╔══════════════════════════════╗"
echo "║   ERPNext 开发环境启动       ║"
echo "╚══════════════════════════════╝"
echo -e "${NC}"

# 1. 检查是否在 bench 目录下
if [ "$(pwd)" != "$BENCH_DIR" ]; then
    warn "当前目录: $(pwd)"
    info "切换到: $BENCH_DIR"
    cd "$BENCH_DIR" || { err "无法进入 $BENCH_DIR"; exit 1; }
fi

# 2. 启动 MariaDB
info "启动 MariaDB..."
if sudo service mariadb status &> /dev/null; then
    ok "MariaDB 已在运行"
else
    sudo service mariadb start && ok "MariaDB 已启动" || err "MariaDB 启动失败"
fi

# 3. 启动 Redis
info "启动 Redis..."
if sudo service redis-server status &> /dev/null; then
    ok "Redis 已在运行"
else
    sudo service redis-server start && ok "Redis 已启动" || err "Redis 启动失败"
fi

# 4. 显示站点信息
echo ""
echo -e "  ${BLUE}站点:${NC}     http://$SITE:8000"
echo -e "  ${BLUE}用户名:${NC}   Administrator"
echo -e "  ${YELLOW}密码:${NC}     你创建站点时设置的密码"
echo ""

# 5. 启动开发服务器
info "启动 bench 开发服务器..."
echo -e "${YELLOW}按 Ctrl+C 停止服务器${NC}"
echo ""

bench start
