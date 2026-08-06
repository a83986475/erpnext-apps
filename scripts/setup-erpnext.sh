#!/bin/bash
# =============================================================================
# ERPNext v16 一键安装脚本（WSL2 / Ubuntu 24.04）
# 版本: 1.0
# 基于 2026-07 真实安装经验编写，已解决所有已知坑点
# =============================================================================
#
# 使用方法：
#   bash setup-erpnext.sh
#
# 说明：
#   - 交互式安装，每一步会提示
#   - 已安装的步骤会自动跳过
#   - 出错时提示修复方法，不会盲目继续
# =============================================================================

set -e  # 遇到错误立即退出

# ── 颜色定义 ──
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ── 辅助函数 ──
info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()   { echo -e "${RED}[ERROR]${NC} $1"; }
step()  { echo -e "\n${GREEN}══════════════════════════════════════════════${NC}"; echo -e "${GREEN}  第 $1 步：$2${NC}"; echo -e "${GREEN}══════════════════════════════════════════════${NC}"; }

# ── 配置（可修改） ──
BENCH_DIR="$HOME/frappe-bench"
SITE_NAME="dev.localhost"
FRAPPE_BRANCH="version-16"
ERPNEXT_BRANCH="version-16"
PYTHON_VERSION="python3.14"
NODE_VERSION="24"

# ── 检查是否以 root 运行 ──
if [ "$EUID" = 0 ]; then
    err "不要以 root 运行此脚本！"
    err "请用普通用户运行（例如你当前的 WSL 用户）"
    err "只有安装系统包时会自动使用 sudo"
    exit 1
fi

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║         ERPNext v16 一键安装脚本                     ║"
echo "║  基于 WSL2 / Ubuntu 24.04 真实安装经验               ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ── 确认开始 ──
read -p "是否开始安装？(y/n): " confirm
if [ "$confirm" != "y" ]; then
    warn "安装取消"
    exit 0
fi

# ══════════════════════════════════════════════════════════════
# 第 1 步：更新系统包
# ══════════════════════════════════════════════════════════════
step 1 "更新系统包列表"

sudo apt update
ok "系统包列表已更新"

# ══════════════════════════════════════════════════════════════
# 第 2 步：安装系统依赖
# ══════════════════════════════════════════════════════════════
step 2 "安装系统依赖"

info "安装编译工具、数据库、缓存等..."

sudo apt install -y \
    git curl wget \
    python3-dev python3-pip python3-setuptools python3-venv \
    mariadb-server mariadb-client \
    redis-server \
    pkg-config \
    libmysqlclient-dev libffi-dev libcairo2 \
    libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 \
    libxslt1-dev libssl-dev libsasl2-dev libldap2-dev \
    libpq-dev libjpeg-dev libpng-dev

ok "系统依赖安装完成"

# 验证关键命令
for cmd in git curl wget python3 pip3 mariadb redis-server pkg-config; do
    if command -v $cmd &> /dev/null; then
        ok "  $cmd 可用"
    else
        warn "  $cmd 未找到（可能已改名或未安装）"
    fi
done

# ══════════════════════════════════════════════════════════════
# 第 3 步：启动 MariaDB 并配置
# ══════════════════════════════════════════════════════════════
step 3 "配置 MariaDB 数据库"

# 启动 MariaDB
sudo service mariadb start || sudo systemctl start mariadb
ok "MariaDB 已启动"

# 先确认 MariaDB 正在运行
if ! sudo service mariadb status &> /dev/null; then
    err "MariaDB 未运行！尝试启动..."
    sudo service mariadb start || { err "MariaDB 启动失败，请手动排查"; exit 1; }
fi
ok "MariaDB 服务运行中"

# 检查认证方式：尝试用 unix_socket（sudo mysql 不需要密码）登录
if sudo mysql -u root -e "SELECT 1;" &> /dev/null; then
    info "MariaDB root 当前使用 unix_socket 认证"
    info "（即只能通过 'sudo mysql' 登录，bench 无法直接连接）"
    echo ""
    info "已将 MariaDB root 认证方式改为密码认证（mysql_native_password）"
    echo ""

    # 询问密码
    while true; do
        read -s -p "请设置 MariaDB root 密码（记住它！）: " DB_PASSWORD
        echo ""
        read -s -p "确认密码: " DB_PASSWORD_CONFIRM
        echo ""

        if [ "$DB_PASSWORD" != "$DB_PASSWORD_CONFIRM" ]; then
            err "两次密码不一致，请重新输入"
        elif [ -z "$DB_PASSWORD" ]; then
            err "密码不能为空，请重新输入"
        else
            break
        fi
    done

    # 改为密码认证
    sudo mysql -u root <<-EOF
        ALTER USER 'root'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
        FLUSH PRIVILEGES;
EOF
    if [ $? -eq 0 ]; then
        ok "MariaDB root 密码已设置（mysql_native_password 认证）"
    else
        err "密码设置失败！请手动执行："
        echo "  sudo mysql -u root -e \"ALTER USER 'root'@'localhost' IDENTIFIED BY '你的密码'; FLUSH PRIVILEGES;\""
        exit 1
    fi
else
    # sudo mysql 失败，可能是因为已经有密码了
    info "MariaDB root 可能已有密码认证"
    echo ""
    if sudo mysql -u root -p"test" -e "SELECT 1;" &> /dev/null; then
        ok "已检测到 root 密码认证（能用密码登录）"
    else
        warn "无法确定 MariaDB 认证状态，后续 bench new-site 时可能需要排查"
        warn "如果报错 'Access denied'，请手动执行："
        echo "  sudo mysql -u root -e \"ALTER USER 'root'@'localhost' IDENTIFIED BY '你的密码'; FLUSH PRIVILEGES;\""
    fi
fi

echo ""
info "验证 MariaDB 连接："
if sudo mysql -u root -e "SELECT VERSION();" &> /dev/null; then
    MARIADB_VER=$(sudo mysql -u root -N -e "SELECT VERSION();")
    ok "MariaDB 版本: $MARIADB_VER"
else
    err "MariaDB 连接失败！请手动排查。"
    err "尝试: sudo mysql -u root"
    exit 1
fi

# ══════════════════════════════════════════════════════════════
# 第 4 步：安装 Python 3.14（如需要）
# ══════════════════════════════════════════════════════════════
step 4 "安装 Python 3.14（ERPNext v16 最新版需要）"

if python3.14 --version &> /dev/null; then
    PY_VER=$(python3.14 --version)
    ok "Python 3.14 已安装: $PY_VER"
else
    info "安装 Python 3.14..."
    sudo apt install -y software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install -y python3.14 python3.14-dev python3.14-venv
    PY_VER=$(python3.14 --version)
    ok "Python 3.14 已安装: $PY_VER"
fi

# ══════════════════════════════════════════════════════════════
# 第 5 步：安装 Node.js 24 + Yarn
# ══════════════════════════════════════════════════════════════
step 5 "安装 Node.js $NODE_VERSION + Yarn"

if command -v nvm &> /dev/null; then
    ok "nvm 已安装"
else
    info "安装 nvm..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    ok "nvm 已安装"
fi

# 重新加载 nvm（确保即使刚安装也可用）
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

if node --version 2>/dev/null | grep -q "v$NODE_VERSION"; then
    NODE_VER=$(node --version)
    ok "Node.js $NODE_VERSION 已安装: $NODE_VER"
else
    info "安装 Node.js $NODE_VERSION..."
    nvm install $NODE_VERSION
    nvm alias default $NODE_VERSION
    NODE_VER=$(node --version)
    ok "Node.js 已安装: $NODE_VER"
fi

# 安装 yarn
if command -v yarn &> /dev/null; then
    YARN_VER=$(yarn --version)
    ok "yarn 已安装: $YARN_VER"
else
    npm install -g yarn
    YARN_VER=$(yarn --version)
    ok "yarn 已安装: $YARN_VER"
fi

# ══════════════════════════════════════════════════════════════
# 第 6 步：安装 uv（Python 包管理工具）
# ══════════════════════════════════════════════════════════════
step 6 "安装 uv（bench 5.x 依赖）"

if command -v uv &> /dev/null; then
    UV_VER=$(uv --version)
    ok "uv 已安装: $UV_VER"
else
    info "安装 uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # uv 可能被安装到 ~/.local/bin
    export PATH="$HOME/.local/bin:$PATH"
    UV_VER=$(uv --version)
    ok "uv 已安装: $UV_VER"
fi

# ══════════════════════════════════════════════════════════════
# 第 7 步：安装 Bench
# ══════════════════════════════════════════════════════════════
step 7 "安装 Bench"

if command -v bench &> /dev/null; then
    BENCH_VER=$(bench --version)
    ok "bench 已安装: $BENCH_VER"
else
    info "安装 pipx..."
    sudo apt install -y pipx
    pipx ensurepath
    export PATH="$HOME/.local/bin:$PATH"

    info "用 pipx 安装 bench..."
    pipx install frappe-bench
    BENCH_VER=$(bench --version)
    ok "bench 已安装: $BENCH_VER"
fi

# ══════════════════════════════════════════════════════════════
# 第 8 步：初始化 Bench + 获取 ERPNext
# ══════════════════════════════════════════════════════════════
step 8 "初始化 Bench + 获取 ERPNext"

if [ -d "$BENCH_DIR" ]; then
    warn "Bench 目录已存在: $BENCH_DIR"
    read -p "是否删除重新初始化？(y/n): " reinit
    if [ "$reinit" = "y" ]; then
        rm -rf "$BENCH_DIR"
        info "已删除旧的 bench 目录"
    else
        info "跳过初始化，使用现有目录"
    fi
fi

if [ ! -d "$BENCH_DIR" ]; then
    info "初始化 bench（使用 frappe $FRAPPE_BRANCH + Python 3.14）..."
    echo ""
    echo -e "${YELLOW}⏱ 这一步需要下载大量依赖，约 3-10 分钟${NC}"
    echo ""

    bench init "$BENCH_DIR" --frappe-branch "$FRAPPE_BRANCH" --python "$PYTHON_VERSION"

    ok "Bench 初始化完成"

    # 进入 bench 目录
    cd "$BENCH_DIR"

    info "获取 ERPNext $ERPNEXT_BRANCH..."
    bench get-app erpnext --branch "$ERPNEXT_BRANCH"
    ok "ERPNext 已获取"
fi

cd "$BENCH_DIR"

# ══════════════════════════════════════════════════════════════
# 第 9 步：创建站点 + 安装 ERPNext
# ══════════════════════════════════════════════════════════════
step 9 "创建开发站点 + 安装 ERPNext"

# 检查站点是否已存在
SITE_EXISTS=false
RECREATE_SITE="n"
if [ -d "sites/$SITE_NAME" ]; then
    SITE_EXISTS=true
    warn "站点 $SITE_NAME 已存在"
    read -p "是否删除并重新创建？(y/n): " RECREATE_SITE
fi

if [ "$SITE_EXISTS" = false ] || [ "${RECREATE_SITE:-n}" = "y" ]; then
    if [ "${RECREATE_SITE:-n}" = "y" ]; then
        bench drop-site "$SITE_NAME" --no-backup 2>/dev/null || true
        rm -rf "sites/$SITE_NAME"
    fi

    echo ""
    info "创建站点 $SITE_NAME..."
    echo -e "${YELLOW}提示：会要求输入 MariaDB root 密码${NC}"
    echo ""

    if ! bench new-site "$SITE_NAME"; then
        echo ""
        warn "创建失败！可能的原因和处理方法："
        warn "1. MariaDB root 密码错误 → 用 --force 重试"
        warn "2. 认证方式问题 → 执行：sudo mysql ALTER USER..."
        echo ""
        bench new-site "$SITE_NAME" --force
    fi

    ok "站点 $SITE_NAME 创建成功"

    echo ""
    info "安装 ERPNext..."
    echo ""
    echo -e "${YELLOW}⚠️  安装 ERPNext 需要 Redis 运行在 11000 端口！${NC}"
    echo -e "${YELLOW}   bench 的 Redis 由 bench start 启动，与系统 Redis 不同。${NC}"
    echo ""
    echo "建议：打开第二个 WSL 终端，运行："
    echo "  cd ~/frappe-bench && bench start"
    echo ""
    echo "然后回到此终端继续。"
    echo ""
    read -p "是否已在新终端运行了 bench start？(y/n): " redis_ready

    if [ "$redis_ready" = "y" ]; then
        bench --site "$SITE_NAME" install-app erpnext
        ok "ERPNext 安装完成！"
    else
        echo ""
        warn "请先在新终端运行 bench start，然后手动执行："
        echo "  cd $BENCH_DIR && bench --site $SITE_NAME install-app erpnext"
        echo ""
        warn "或者之后随时可以运行上面的命令来安装 ERPNEXT"
        # 不退出，只提示，让用户之后自己装
    fi
else
    info "站点 $SITE_NAME 已存在，跳过创建"
    info "如果站点创建不完整，可以运行：bench --site $SITE_NAME reinstall"
fi

# ══════════════════════════════════════════════════════════════
# 完成
# ══════════════════════════════════════════════════════════════
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║            安装完成！                               ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  站点地址: ${BLUE}http://$SITE_NAME:8000${NC}"
echo -e "  用户名:   Administrator"
echo -e "  密码:     你设置的 Admin 密码"
echo ""
echo "以后每次打开："
echo "  1. wsl"
echo "  2. sudo service mariadb start && sudo service redis-server start"
echo "  3. cd ~/frappe-bench && bench start"
echo ""
echo -e "  或者用快速启动脚本：${YELLOW}bash start-dev.sh${NC}"
echo ""

# ── 提示将 PATH 写入 bashrc ──
if ! grep -q "\.local/bin" "$HOME/.bashrc" 2>/dev/null; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    ok "已将 ~/.local/bin 加入 PATH"
fi
if ! grep -q "NVM_DIR" "$HOME/.bashrc" 2>/dev/null; then
    echo 'export NVM_DIR="$HOME/.nvm"' >> "$HOME/.bashrc"
    echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> "$HOME/.bashrc"
    ok "已将 nvm 配置写入 ~/.bashrc"
fi

info "请重新加载 shell 配置：source ~/.bashrc"
