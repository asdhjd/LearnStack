# LearnStack 项目部署指南

## 项目概述

LearnStack 是一个学习资源管理平台，包含以下组件：
- **前端**: Vue 3 + Vite + Element Plus
- **后端**: Django 4.2 + Django REST Framework
- **数据库**: MySQL 8.0

## 部署方案

### 方案一：Docker Compose 部署（推荐）

这是最简单、最可靠的部署方式，适合展示给 HR 看。

#### 前置条件

1. 服务器已安装 Docker 和 Docker Compose
2. 服务器开放端口 80（HTTP）

#### 部署步骤

1. **克隆项目到服务器**
```bash
git clone <项目仓库地址>
cd LearnStack
```

2. **启动服务**
```bash
docker-compose up -d
```

3. **等待服务启动**

首次启动需要下载镜像并初始化数据库，可能需要几分钟。

4. **访问网站**

打开浏览器访问：`http://服务器IP`

#### 服务说明

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端 (Nginx) | 80 | 用户访问的主端口 |
| 后端 (Django) | 8000 | API 服务（内部端口） |
| 数据库 (MySQL) | 3306 | 数据存储（内部端口） |

#### 停止服务
```bash
docker-compose down
```

#### 查看日志
```bash
docker-compose logs -f
```

#### 重启服务
```bash
docker-compose restart
```

### 方案二：传统服务器部署

#### 环境要求

- Python 3.8+
- Node.js 18+
- MySQL 8.0
- Nginx

#### 后端部署

1. **安装依赖**
```bash
cd learnstack_backend
pip install -r requirements.txt
```

2. **配置数据库**
```bash
mysql -u root -p
CREATE DATABASE learnstack CHARACTER SET utf8mb4;
```

3. **迁移数据库**
```bash
python manage.py migrate
```

4. **收集静态文件**
```bash
python manage.py collectstatic
```

5. **启动 Gunicorn**
```bash
gunicorn --bind 0.0.0.0:8000 learnstack_backend.wsgi
```

#### 前端部署

1. **安装依赖**
```bash
cd learnstack_frontend
npm install
```

2. **构建项目**
```bash
npm run build
```

3. **配置 Nginx**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /path/to/learnstack_frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /media/ {
        alias /path/to/learnstack_backend/media/;
    }

    location /static/ {
        alias /path/to/learnstack_backend/staticfiles/;
    }
}
```

## 环境变量配置

### 后端环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| DEBUG | False | 是否开启调试模式 |
| SECRET_KEY | django-insecure-... | 密钥，生产环境务必修改 |
| DATABASE_NAME | learnstack | 数据库名 |
| DATABASE_USER | learnstack_user | 数据库用户名 |
| DATABASE_PASSWORD | learnstack_password | 数据库密码 |
| DATABASE_HOST | db | 数据库主机 |
| DATABASE_PORT | 3306 | 数据库端口 |

### 前端环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| VITE_API_BASE_URL | /api | API 基础地址 |

## 数据库初始化

项目已包含 `learnstack.sql` 文件，首次部署时 Docker Compose 会自动执行该文件初始化数据库。

如果需要手动导入数据：
```bash
mysql -u root -p learnstack < learnstack.sql
```

## 生产环境注意事项

1. **修改 SECRET_KEY**：务必在生产环境设置安全的密钥
2. **关闭 DEBUG**：确保 DEBUG=False
3. **配置域名**：建议使用域名而非 IP 地址
4. **配置 HTTPS**：使用 Let's Encrypt 配置 SSL
5. **备份数据库**：定期备份 MySQL 数据
6. **配置防火墙**：只开放必要端口

## 部署检查清单

- [ ] Docker 和 Docker Compose 已安装
- [ ] 端口 80 已开放
- [ ] SECRET_KEY 已修改
- [ ] DEBUG 已关闭
- [ ] 数据库密码已修改
- [ ] 数据备份策略已配置

## 技术亮点（简历展示）

1. **容器化部署**：使用 Docker Compose 实现一键部署
2. **环境变量管理**：通过环境变量实现配置与代码分离
3. **前后端分离**：前端静态文件通过 Nginx 服务，API 通过反向代理
4. **生产级配置**：使用 Gunicorn 替代 Django 开发服务器
5. **数据库持久化**：使用 Docker Volume 实现数据持久化
6. **跨域配置**：支持开发和生产环境的不同 CORS 策略