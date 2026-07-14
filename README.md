# LearnStack - 一站式学习资源平台

LearnStack 是一个面向开发者的一站式学习资源平台，提供技术分类浏览、学习路径规划、资源推荐和社区问答等功能。

## 功能特性

### 🎯 核心功能

- **技术分类管理** - 按技术栈和子分类浏览学习资源
- **学习路径规划** - 为不同阶段的开发者提供系统化学习路线
- **资源库** - 包含视频、文章、文档、书籍等多种类型的学习资源
- **收藏功能** - 收藏喜欢的资源和分类，方便后续学习
- **社区问答** - 提出问题、回答问题、讨论技术话题

### 🛠️ 管理功能

- **资源审核** - 管理员审核用户提交的资源
- **分类管理** - 管理技术分类和子分类
- **用户管理** - 用户权限和角色管理
- **资源请求** - 处理用户的资源请求

## 技术栈

### 后端技术

| 技术 | 版本 | 说明 |
|------|------|------|
| Django | 4.2.21 | 后端框架 |
| Django REST Framework | 3.14.0 | REST API 框架 |
| SimpleJWT | 5.3.0 | JWT 认证 |
| MySQL | 8.0 | 数据库 |
| PyMySQL | 1.1.1 | MySQL 驱动 |
| Gunicorn | 21.2.0 | WSGI 服务器 |

### 前端技术

| 技术 | 版本 | 说明 |
|------|------|------|
| Vue.js | 3.5+ | 前端框架 |
| Vite | 6.2+ | 构建工具 |
| Element Plus | 2.11+ | UI 组件库 |
| Vue Router | 4.5+ | 路由管理 |
| Pinia | 3.0+ | 状态管理 |
| Axios | 1.9+ | HTTP 请求 |
| Chart.js | 4.5+ | 图表库 |

### 部署技术

- **Docker Compose** - 容器化部署
- **Nginx** - 反向代理
- **MySQL** - 数据库服务

## 项目结构

```
LearnStack/
├── learnstack_backend/          # 后端 Django 项目
│   ├── categories/              # 技术分类模块
│   ├── community/               # 社区问答模块
│   ├── favorites/               # 收藏夹模块
│   ├── learning_paths/          # 学习路径模块
│   ├── resources/               # 资源库模块
│   ├── users/                   # 用户管理模块
│   ├── learnstack_backend/      # 项目配置
│   ├── manage.py                # Django 管理命令
│   ├── Dockerfile               # 后端 Docker 配置
│   ├── entrypoint.sh            # 启动脚本
│   └── requirements.txt         # Python 依赖
│
├── learnstack_frontend/         # 前端 Vue 项目
│   ├── src/
│   │   ├── components/          # 公共组件
│   │   ├── config/              # 配置文件
│   │   ├── router/              # 路由配置
│   │   ├── services/            # API 服务
│   │   ├── stores/              # 状态管理
│   │   ├── utils/               # 工具函数
│   │   └── views/               # 页面视图
│   ├── nginx.conf               # Nginx 配置
│   ├── Dockerfile               # 前端 Docker 配置
│   └── package.json             # Node.js 依赖
│
├── docker-compose.yml           # Docker Compose 配置
├── .env.example                 # 环境变量模板
└── README.md                    # 项目说明
```

## 快速开始

### 环境要求

- Docker 20.10+
- Docker Compose 2.0+

### 1. 克隆项目

```bash
git clone https://github.com/asdhjd/LearnStack.git
cd LearnStack
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置以下关键变量：

```bash
# Django 配置
SECRET_KEY=your-secret-key-here-generate-a-new-one-for-production
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,backend

# 数据库配置
DATABASE_NAME=learnstack
DATABASE_USER=learnstack_user
DATABASE_PASSWORD=LearnStack@123
DATABASE_HOST=db
DATABASE_PORT=3306

# MySQL Root 密码
MYSQL_ROOT_PASSWORD=Root@123456
```

### 3. 启动服务

```bash
docker compose up -d --build
```

### 4. 初始化数据

首次启动时，数据库会自动导入 `learnstack.sql` 文件中的初始数据。

### 5. 访问服务

- **前端页面**: http://localhost
- **后端 API**: http://localhost/api/
- **管理后台**: http://localhost/admin/

## API 接口

### 用户认证

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/users/login/` | POST | 用户登录 |
| `/api/users/register/` | POST | 用户注册 |
| `/api/users/profile/` | GET | 获取用户信息 |

### 技术分类

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/categories/` | GET | 获取所有分类 |
| `/api/categories/{id}/` | GET | 获取分类详情 |
| `/api/categories/hotsubcategories/` | GET | 获取热门子分类 |

### 学习路径

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/learning_paths/` | GET | 获取所有学习路径 |
| `/api/learning_paths/{id}/` | GET | 获取学习路径详情 |

### 资源库

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/resources/` | GET | 获取资源列表 |
| `/api/resources/{id}/` | GET | 获取资源详情 |
| `/api/resources/` | POST | 提交资源（需认证） |

### 社区问答

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/questions/` | GET | 获取问题列表 |
| `/api/questions/{id}/` | GET | 获取问题详情 |
| `/api/questions/` | POST | 提问（需认证） |

### 收藏夹

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/favorites/` | GET | 获取收藏列表 |
| `/api/favorites/` | POST | 添加收藏（需认证） |

## 开发指南

### 后端开发

```bash
# 进入后端目录
cd learnstack_backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
python manage.py runserver 0.0.0.0:8000
```

### 前端开发

```bash
# 进入前端目录
cd learnstack_frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev
```

### 测试

```bash
# 后端测试
cd learnstack_backend
python manage.py test

# 前端测试
cd learnstack_frontend
npm run test:unit
```

## 部署

### 生产环境部署

1. 配置 `.env` 文件，设置 `DEBUG=False` 和生产环境域名
2. 构建并启动容器：

```bash
docker compose up -d --build
```

### 数据库备份

```bash
# 备份数据库
docker exec learnstack_db mysqldump -u learnstack_user -pLearnStack@123 learnstack > backup.sql

# 恢复数据库
docker cp backup.sql learnstack_db:/backup.sql
docker exec learnstack_db mysql -u learnstack_user -pLearnStack@123 learnstack < /backup.sql
```

## 配置说明

### Nginx 配置

前端 Nginx 配置位于 `learnstack_frontend/nginx.conf`，主要包含：

- 静态资源服务
- API 请求代理到后端
- 媒体文件代理

### CORS 配置

后端已配置 CORS 中间件，允许前端跨域请求。

### JWT 认证

使用 `djangorestframework-simplejwt` 提供 JWT 认证，Token 有效期为 5 分钟，刷新 Token 有效期为 1 天。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

### 提交规范

- 提交信息格式：`类型: 描述`
- 类型：`feat`（新功能）、`fix`（修复）、`docs`（文档）、`style`（样式）、`refactor`（重构）

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过以下方式联系：

- GitHub Issues: https://github.com/asdhjd/LearnStack/issues