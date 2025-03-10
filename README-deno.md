# ETF 数据分析桌面应用

基于 Deno + Fresh + Tauri 构建的 ETF 数据分析桌面应用。

## 技术栈

- **后端**: Deno + Fresh (Web 框架)
- **前端**: Preact + Twind (CSS-in-JS)
- **桌面**: Tauri (跨平台桌面框架)
- **图表**: ECharts
- **数据**: adata (A股数据)

## 项目结构

```
app-desktop/
├── src/                    # 源代码目录
│   ├── components/        # 组件
│   │   ├── Chart.tsx     # 图表组件
│   │   ├── Search.tsx    # 搜索组件
│   │   └── Layout.tsx    # 布局组件
│   ├── routes/           # 路由
│   │   ├── index.tsx    # 主页
│   │   └── api/         # API 路由
│   │       └── etf.ts   # ETF 数据 API
│   ├── utils/           # 工具函数
│   │   ├── etf.ts      # ETF 数据处理
│   │   └── date.ts     # 日期处理
│   └── types/          # 类型定义
│       └── etf.ts      # ETF 相关类型
├── static/             # 静态资源
├── deno.json          # Deno 配置
├── fresh.config.ts    # Fresh 配置
├── import_map.json    # 依赖映射
└── tauri/            # Tauri 配置和原生代码
```

## 重构步骤

1. **环境搭建**
   - 安装 Deno
   - 安装 Tauri CLI
   - 创建 Fresh 项目

2. **后端迁移**
   - 将 Flask 路由迁移到 Fresh 路由
   - 使用 Deno 重写数据处理逻辑
   - 实现 ETF 数据 API

3. **前端重构**
   - 使用 Preact 组件化重构页面
   - 实现响应式布局
   - 集成 ECharts 图表

4. **桌面应用集成**
   - 配置 Tauri
   - 实现本地数据缓存
   - 添加系统托盘功能

## 主要改进

1. **性能优化**
   - 使用 Deno 的原生 TypeScript 支持
   - 组件级别的代码分割
   - 数据本地缓存

2. **开发体验**
   - TypeScript 类型检查
   - 热重载支持
   - 开发工具集成

3. **用户体验**
   - 更快的启动速度
   - 离线支持
   - 原生系统集成

## 开发流程

1. **安装依赖**
```bash
# 安装 Deno
curl -fsSL https://deno.land/x/install/install.sh | sh

# 安装 Tauri CLI
cargo install tauri-cli

# 创建项目
deno run -A -r https://fresh.deno.dev app-desktop
```

2. **启动开发服务器**
```bash
# 进入项目目录
cd app-desktop

# 启动开发服务器
deno task start
```

3. **构建桌面应用**
```bash
# 构建
deno task tauri build
```
