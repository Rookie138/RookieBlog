# 部署到阿里云（Ubuntu 22.04/24.04 · 2C2G）上线手册

目标拓扑（`example.com` 请全局替换为你的域名，`SERVER_IP` 为服务器公网 IP）：

```
用户浏览器
   │ https://example.com        （博客前台 frontend，静态文件）
   │ https://admin.example.com  （管理端 frontend_manage，静态文件）
   ▼
nginx（80/443，静态 + 反向代理 + SPA fallback + HTTPS 证书）
   │  /common-articles ──┐
   │  /auth ─────────────┤──► 127.0.0.1:8000  FastAPI(uvicorn, systemd: blog-backend)
   │  /manage-articles ──┘
   ▼
MySQL 8（127.0.0.1，仅本机）
```

前端走 nginx 同源反代 → **不需要跨域，后端 CORS 配置可不动**。
两个前端都在本地构建好再上传 `dist/`，**服务器不装 Node**（省内存）。

---

## 0. 阿里云控制台与 Cloudflare（先做，服务器外）

1. **阿里云安全组**：放行入方向 `22 / 80 / 443`（只放这几个，MySQL 3306 **不要**放公网）。
2. **Cloudflare**（你的域名托管在 CF）：
   - 进入 DNS → Records，确保有两条 A 记录，均指向服务器公网 IP：
     - 名称 `@`（根域）→ `SERVER_IP`
     - 名称 `admin` → `SERVER_IP`
   - **把云朵图标点成灰色（仅 DNS / DNS only）**，不要开橙色代理——初期直连最简单，证书、排错都不被 CF 干扰。等 HTTPS 全部就绪后想上 CDN/代理，再开橙色并把 CF SSL/TLS 模式设为 **Full (strict)**。
   - 本机验证解析：`ping example.com` 或 `nslookup example.com` 返回你的服务器 IP 即 OK。

## 1. 服务器初始化（ssh 登录后执行，root 或 sudo）

```bash
# 1.1 基础更新 + swap（2C2G 建议 2G swap，防内存打满）
apt update && apt upgrade -y
fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
sysctl vm.swappiness=10   # 临时；持久化见下文“可选优化”

# 1.2 装软件：nginx / MySQL / uv（后端用 uv 管理 venv，与本地一致）
apt install -y nginx mysql-server curl git
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# 1.3 防火墙（服务器外还有安全组这层，ufw 是第二道）
ufw allow OpenSSH && ufw allow 80 && ufw allow 443 && ufw --force enable
```

> MySQL 安装后 Ubuntu 默认 root 走 `auth_socket`：`sudo mysql` 即可进，无需密码。

## 2. 上传代码与前端产物

**在你自己电脑（Windows，PowerShell）执行**，把四个东西传上去：
```powershell
# 若 dist 不存在，先在本地各执行一次 npm run build（frontend 与 frontend_manage）
scp -r .\backend user@SERVER_IP:/opt/blog/backend
scp -r .\frontend\dist user@SERVER_IP:/opt/blog/frontend-dist
scp -r .\frontend_manage\dist user@SERVER_IP:/opt/blog/manage-dist
scp .\deploy\nginx\blog.conf user@SERVER_IP:/tmp/blog.conf
scp .\deploy\systemd\blog-backend.service user@SERVER_IP:/tmp/blog-backend.service
```
服务器上放好目录并授权（以 www-data 运行后端，静态文件也归它读）：
```bash
mkdir -p /opt/blog/backend /opt/blog/frontend-dist /opt/blog/manage-dist
# 把上面 scp 的内容移动进去（示例：cp -r /tmp/backend/* /opt/blog/backend/ …）
chown -R www-data:www-data /opt/blog
```
> 本地构建时若改过代码，记得先重新 `npm run build` 再上传。

## 3. 后端环境（.env.prod、依赖、建库、迁移、管理员）

```bash
# 3.1 环境变量模板 → 实际文件
cp /opt/blog/backend/env/.env.prod.example /opt/blog/backend/env/.env.prod
nano /opt/blog/backend/env/.env.prod
#   必改两项：
#   SECRET_KEY="$(openssl rand -hex 32)"        ← 生成强密钥填进去
#   DATABASE_PASSWORD="$(openssl rand -hex 16)" ← 强密码，记下来下一步用
#   DATABASE_HOST 固定 127.0.0.1（不要写 localhost，asyncmy 会走 socket 连不上）

# 3.2 建库建账号（root 用 auth_socket 免密）
sudo mysql <<'SQL'
CREATE DATABASE blog DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'blog'@'127.0.0.1' IDENTIFIED BY '上一步生成的 DATABASE_PASSWORD';
GRANT ALL PRIVILEGES ON blog.* TO 'blog'@'127.0.0.1';
FLUSH PRIVILEGES;
SQL

# 3.3 安装依赖（锁定版本）
#   说明：项目要求 Python >=3.12。Ubuntu 24.04 自带 3.12；
#   若用 22.04（自带 3.10），uv 会自动下载托管的 Python 3.12，无需手动装。
cd /opt/blog/backend
export ENVIRONMENT=prod
uv sync --frozen

# 3.4 建表（alembic 迁移）
uv run alembic upgrade head

# 3.5 初始化管理员（密码走 argon2 哈希，别再存明文！）
uv run python -c "
from app.utils.hash_util import PwdHashUtil
from app.config.setting import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.api.auth.model import User
engine = create_engine(settings.DB_URI)
Session = sessionmaker(bind=engine, expire_on_commit=False)
with Session() as s:
    s.query(User).filter(User.username == 'admin').delete()
    s.add(User(username='admin', password=PwdHashUtil.hash_password('改成你的强密码'), name='admin'))
    s.commit()
print('admin ready')
"
```

## 4. 后端 systemd 服务

```bash
cp /tmp/blog-backend.service /etc/systemd/system/blog-backend.service
nano /etc/systemd/system/blog-backend.service   # 核对路径；改密码后无需改这里
systemctl daemon-reload
systemctl enable --now blog-backend
systemctl status blog-backend          # active (running)
curl http://127.0.0.1:8000/            # {"message":"Hello World"}
```

## 5. nginx + HTTPS

```bash
# 5.1 先放 http 配置（含全部 location，certbot 稍后自动补 https）
#     先 sed 把里面的 example.com 换成你的域名
sed -i 's/example\.com/你的域名/g' /tmp/blog.conf
cp /tmp/blog.conf /etc/nginx/sites-available/blog.conf
ln -s /etc/nginx/sites-available/blog.conf /etc/nginx/sites-enabled/blog.conf
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# 5.2 此时应已可 http 访问：
#   curl http://example.com/                → 前台首页 HTML
#   curl http://admin.example.com/login     → 管理端登录页 HTML

# 5.3 签发证书（certbot --nginx 会自动改配置加 443 + 跳转）
apt install -y certbot python3-certbot-nginx
certbot --nginx -d example.com -d www.example.com -d admin.example.com
#   按提示填邮箱、同意条款；成功后自动续期由系统 timer 负责，无需手动

# 5.4 验证
curl -I https://example.com/                     # 200
curl -I https://admin.example.com/login          # 200
curl -X POST https://admin.example.com/auth/token \
     -d 'username=admin&password=你的强密码'      # 返回 access_token 即全链路通
```

## 6. 访问测试清单

- [ ] `https://example.com` 打开前台，能看文章
- [ ] 管理端 `https://admin.example.com` 登录 → 新建草稿 → 发布 → 前台立即可见
- [ ] 刷新/深链接：`https://example.com/articles/xxx`、`https://admin.example.com/articles/new` 不 404（SPA fallback 生效）
- [ ] 手机访问正常（响应式样式已内置）

## 7. 日常维护

```bash
# 备份数据库（crontab -e 加一行，每天凌晨 3 点）
# 3 0 * * * mysqldump -ubackup -p'密码' blog > /var/backups/blog_$(date +\%F).sql 2>/dev/null

# 更新前端：本地 npm run build → scp dist → 无需动 nginx
# 更新后端：本地改好 → scp backend 到 /opt/blog/backend → systemctl restart blog-backend
# 查后端日志：journalctl -u blog-backend -f
# 查 nginx 错误：tail -f /var/log/nginx/error.log
```

## 8. 常见问题

| 现象 | 处理 |
| --- | --- |
| certbot 报 80 连不上 | 阿里云安全组没放 80；先放行 |
| 502 Bad Gateway | 后端没起来：`systemctl status blog-backend` / `journalctl -u blog-backend -e`；或后端端口改过 |
| 登录 400/500 | 确认 `.env.prod` 的 SECRET_KEY 与 DATABASE_PASSWORD 已填，且第 3.5 步管理员密码哈希后落库 |
| 前台 404（深链接） | nginx 里 `try_files ... /index.html` 缺失 |
| 想开 Cloudflare 橙色代理 | 先把 CF SSL/TLS 设为 Full(strict)，再开代理，避免证书循环 |
| MySQL 连不上 | 确认 DATABASE_HOST=127.0.0.1 且用户为 blog@127.0.0.1 |

## 可选优化（2C2G 建议）
```bash
# swap 持久化策略：/etc/sysctl.conf 加 vm.swappiness=10
# 内存占用大头是 MySQL，可调小 buffer pool：/etc/mysql/mysql.conf.d/mysqld.cnf
#   innodb_buffer_pool_size = 256M
# 全部是 python 单机小站：uvicorn 单进程即可（systemd 单元已是）
```
