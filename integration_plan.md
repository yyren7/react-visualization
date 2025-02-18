@/plan.md 我想做的其实是和图片里显示的那样，把现在的项目做成一个cline或者cursor那样的ai编辑器。我要在quick_fcp/src 这个项目的基础上做增量开发，给我具体详细的开发执行方案和新的系统架构，写在一个新的md文件里。
# 全栈架构整合与迁移方案 (修订版 - 保留 Next.js)

## 一、现有架构分析

### 1.1 前端 (Next.js)

*   **主入口**: `src/pages/index.js`，使用 React, Blockly, Konva, react-table, react-sidebar。
*   **状态管理**: `src/context/AppContext.js` (React Context)。
*   **自定义Hook**: `src/hooks/useDeepCompareEffect.js`。
*   **UI组件**: `src/lib/mainParts/*`, `src/lib/sidebarParts/*`, `src/lib/myblockly/*`。
*   **配置文件**: `public/config/*.yaml`。
*   **API 路由**: `src/pages/api/*` (Next.js 特性)。
*   **启动脚本**: `src/app/npm_run.py` (执行 `npm run start`，即 `next start`)。

### 1.2 后端 (Flask + Celery + Redis)

*   **API 服务**: `src/app/program_handler.py` (Flask 应用)。
*   **异步任务**: `src/app/celery_tasks_worker.py` (Celery worker)。
*   **任务触发**: `src/app/celery_tasks_producer.py`。
*   **程序执行**: `src/app/auto.py`, `src/app/man.py`, `src/app/comm.py`。
*   **日志**: `program_handler_logs/`, `celery_tasks_logs/`, `npm_run_logs/`。
*   **工具**: `lib/utility/custom_logger.py`。

## 二、目标架构 (修改后)

*   **前端**: Next.js + React + React Flow + Zustand + Monaco Editor （**保留 Next.js**)
*   **后端**: FastAPI + PostgreSQL + Celery + Redis + Pydantic V2

## 三、迁移策略 (修改后)

### 3.1 前端 (Next.js 保留)

1.  **框架保留**: **保留 Next.js** 作为前端框架。
    *   **API 路由迁移**:  **移除 Next.js 特有的 API 路由** (`src/pages/api/*`)，迁移到后端 FastAPI。前端通过 `fetch` 或 `axios` 等库与 FastAPI 后端 API 交互。
    *   **Next.js 特性**:  继续利用 Next.js 的路由、组件结构和构建优化。不再需要移除 `getInitialProps` 等特性，但需要确保新的组件和逻辑与 Next.js 兼容。
    *   **`src/pages/index.js`**:  继续作为 Next.js 页面，整合新的 React 组件和逻辑。

2.  **组件复用**:
    *   Blockly 编辑器逻辑 (主要在 `src/lib/myblockly/*` 和 `src/pages/index.js` 中)。
    *   Konva 画布组件 (主要在 `src/pages/index.js` 中)。
    *   状态管理逻辑 (部分可从 `src/context/AppContext.js` 迁移)。
    *   UI 组件 (尽可能复用 `src/lib/mainParts/*` 和 `src/lib/sidebarParts/*`)。

3.  **新增组件**:
    *   工作流可视化层 (基于 React Flow)。
    *   LLM 智能建议浮窗。
    *   自然语言交互界面。

### 3.2 后端

1.  **框架迁移**: 从 Flask 迁移到 FastAPI。
    *   `src/app/program_handler.py` 中的 API 路由迁移到 FastAPI。
    *   保留 Celery (`src/app/celery_tasks_worker.py`) 和 Redis 的使用。

2.  **模块映射**:

    | 现有模块                       | 新架构模块                   | 备注                               |
    | ------------------------------ | ---------------------------- | ---------------------------------- |
    | `program_handler.py`           | API 网关层 + 业务逻辑层      | Flask 路由迁移到 FastAPI           |
    | `celery_tasks_worker.py`       | 工作流引擎层 + LLM 集成层    | 保留 Celery 任务                   |
    | `auto.py`/`man.py`/`comm.py` | 代码生成层 + 设备抽象层       | 抽象设备交互，复用部分执行逻辑     |
    | `lib/utility/custom_logger.py` | (保留)                       |                                    |
    | `public/config/*.yaml`         | (保留)                       |                                    |

3.  **新增模块**:

    *   LLM 集成层 (多模型路由、prompt 工程)。
    *   工作流引擎层 (节点注册、语法验证、拓扑排序)。
    *   代码生成层 (模板引擎、API 调用链构建)。
    *   设备抽象层 (统一不同机器人厂商的 API)。

## 四、目录结构 (调整 - 保持 Next.js 结构)

```
react-visualization/
├── frontend/                 # 前端 (Next.js) - 目录名保持 frontend 更通用
│   ├── public/
│   │   └── config/          # 移植 YAML 配置
│   └── src/
│       ├── components/      # React 组件
│       │   ├── FlowEditor/  # React Flow 工作流编辑器 (新增)
│       │   ├── BlocklyEditor/ # Blockly 编辑器 (移植)
│       │   ├── KonvaCanvas/  # Konva 画布 (移植)
│       │   ├── ChatInterface/ # 自然语言交互 (新增)
│       │   └── ...
│       ├── hooks/           # 自定义 Hooks
│       ├── lib/             # 工具函数、Blockly/Konva 配置等
│       ├── context/         # 状态管理 (Zustand)
│       ├── pages/           # Next.js 页面 - **保持 pages 目录**
│       │   └── index.js     # 应用入口 - **保持 index.js**
│       └── _app.js          # Next.js _app.js - **保持 _app.js**
├── backend/                  # 后端 (FastAPI)
│   ├── app/
│   │   ├── api/             # API 网关层
│   │   ├── logic/           # 业务逻辑层
│   │   ├── llm/             # LLM 集成层
│   │   ├── engine/          # 工作流引擎
│       │   ├── codegen/         # 代码生成层
│       │   ├── persistence/     # 数据持久化层
│       │   ├── external/        # 外部系统适配 (设备抽象层)
│       │   ├── core/            # Celery, Redis, 日志等核心逻辑
│       │   ├── main.py          # 应用入口
│       │   ├── config.py        # 配置
│       │   └── utils.py         # 工具函数
└── shared/                   # 共享资源 (可选)
    └── protocols/          # 设备协议定义
```

## 五、关键集成点 (细化)

1.  **Blockly 与 React Flow 集成**:
    *   Blockly 生成的 XML 转换为 React Flow 可识别的节点和边数据结构。
    *   React Flow 的交互事件 (节点拖拽、连接等) 反向更新 Blockly 工作区。

2.  **LLM 集成**:
    *   前端提供输入接口 (文本框、语音输入)。
    *   **前端调用后端 FastAPI 提供的 LLM API**。
    *   后端调用 LLM API (GPT-4, Claude 3 等)。
    *   LLM 输出解析为结构化数据 (JSON Schema)。
    *   LLM 建议与 Blockly/React Flow 集成。

3.  **设备抽象层**:
    *   定义统一的设备接口 (`DeviceAdapter` 类)。
    *   为不同厂商的机器人 (Dobot, Hitbot, Fairino, IAI, Robodk) 实现具体的驱动 (`ModbusDriver`, `ROSDriver`, `URDriver` 等)。
    *   复用 `src/app/comm.py` 中的部分通信逻辑。

4.  **代码生成**:
    - 将 `auto.py` 的逻辑迁移到 `codegen` 中。

## 六、实施路线图

1.  **阶段一：基础架构迁移 (2-3 周) (修改)**
    *   [x] **保留 Next.js 项目**:  在现有 Next.js 项目基础上进行修改，而不是创建新的 React 项目。
    *   [x] 移植 Blockly 编辑器 (包括自定义块、工具箱、主题)。
    *   [x] 移植 Konva 画布。
    *   [x] 搭建 FastAPI 后端框架。
    *   [x] 迁移 Celery worker 和 Redis 集成。
    *   [x] **迁移 Flask API 路由到 FastAPI 后端**。
    *   [x] 迁移 YAML 配置系统。
    *   [x] 迁移日志模块。

2.  **阶段二：核心功能集成 (3-4 周)**
    *   [ ] 实现 React Flow 工作流可视化。
    *   [ ] 集成 Blockly 与 React Flow。
    *   [ ] 实现 LLM 集成 (包括 prompt 工程)。
    *   [ ] 构建设备抽象层。
    *   [ ] 实现代码生成模块 (基于模板引擎)。
    *   [ ] 实现工作流引擎 (节点注册、验证、执行)。

3.  **阶段三：完善与优化 (1-2 周)**
    *   [ ] 实现多轮对话式参数配置界面。
    *   [ ] 实现工作流版本管理。
    *   [ ] 增加安全机制 (沙箱执行、静态代码分析)。
    *   [ ] 性能测试与优化。
    *   [ ] 编写文档。