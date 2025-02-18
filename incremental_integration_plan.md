# Quick FCP 增量开发方案

## 目标

在现有 Quick FCP 项目基础上进行增量开发，**保留 Next.js 前端框架** 和 **Flask 后端框架**，逐步添加新功能，并确保系统的稳定性和可维护性。

## 现有项目分析

Quick FCP 项目是一个基于 Next.js 前端和 Flask 后端的应用，使用 Celery 进行异步任务处理。

- **前端 (Next.js):**
    - 位于 `src/pages` 目录，使用 React 和 JavaScript。
    - 使用 `src/context/AppContext.js` 进行全局状态管理。
    - UI 组件位于 `src/lib` 目录。
- **后端 (Flask):**
    - 位于 `src/app/program_handler.py`，使用 Flask 提供 API 接口。
    - 使用 Celery (`src/app/celery_tasks_worker.py`) 处理后台任务。
    - Python 脚本位于 `src/app` 目录 (`auto.py`, `man.py`, `comm.py`)。

## 增量开发策略

1. **模块化开发:**
    - 将新功能划分为独立的模块，每个模块包含前端组件、后端 API 和 Celery 任务（如果需要）。
    - 在 `src/lib` 目录下创建新的子目录来组织新的前端模块 (例如 `src/lib/new_feature_parts`)。
    - 在 `src/app` 目录下创建新的 Python 文件或子目录来组织新的后端模块 (例如 `src/app/new_feature_module.py`)。

2. **API 优先:**
    - 新功能的前端组件应通过 API 与后端交互。
    - 在 `src/pages/api` 目录下创建新的 API 路由处理新功能的后端请求。
    - 保持 API 接口的清晰和一致性，方便前端调用和维护。

3. **状态管理扩展:**
    - 如果新功能需要新的全局状态，可以扩展 `src/context/AppContext.js`，添加新的 Context 和 Provider。
    - 尽量复用现有的状态管理逻辑，避免状态管理的过度复杂化。

4. **组件复用:**
    - 尽量复用 `src/lib` 目录下现有的 UI 组件和工具函数。
    - 创建新的组件时，应考虑其通用性和可复用性，方便在其他模块中使用。

5. **测试驱动开发 (TDD):**
    - 为新功能编写单元测试和集成测试，确保代码质量和功能正确性。
    - 前端组件可以使用 Jest 和 React Testing Library 进行测试。
    - 后端 API 和 Celery 任务可以使用 pytest 进行测试。

6. **逐步部署:**
    - 将新功能逐步部署到生产环境，先进行小范围测试，再逐步扩大用户范围。
    - 使用 Feature Flags 来控制新功能的上线和下线，方便进行 A/B 测试和灰度发布。

## 技术栈选择

- **前端:** 保持 Next.js 和 React，使用 JavaScript 或 TypeScript 进行开发。
- **后端:** 保持 Flask 框架，使用 Python 进行开发。
- **异步任务:** 继续使用 Celery。
- **状态管理:** 继续使用 React Context 或考虑 Zustand (如 `plan.md` 中建议)。
- **数据持久化:**  根据新功能的需求选择合适的数据库，可以继续使用 PostgreSQL 或考虑其他数据库。

## 开发流程

1. **需求分析:** 详细分析新功能的需求，明确功能范围和技术方案。
2. **模块设计:** 将新功能划分为模块，设计模块的接口和组件。
3. **API 设计:** 设计后端 API 接口，定义请求和响应的数据格式。
4. **编码实现:** 前后端分别实现新功能模块。
5. **测试:** 编写单元测试和集成测试，进行充分测试。
6. **代码审查:** 进行代码审查，确保代码质量。
7. **部署:** 逐步部署新功能到生产环境。
8. **监控和维护:** 监控新功能的运行状态，及时修复 bug 和优化性能。

## 具体模块开发内容示例

### 示例模块 1:  **新的机器人控制面板**

**功能描述:**  添加一个新的控制面板，用于控制特定型号的机器人，例如 Dobot CR 系列。该面板应包含机器人的实时状态显示、运动控制按钮、参数配置等功能。

**前端开发内容 (Next.js, React):**

- **模块目录:** 在 `src/lib` 下创建 `src/lib/dobot_control_parts` 目录。
- **组件设计:**
    - `DobotControlPanel.js`:  主控制面板组件，包含状态显示、控制按钮等。
    - `DobotStatusDisplay.js`:  显示机器人实时状态 (例如坐标、关节角度、运行模式等)。
    - `DobotMotionControl.js`:  包含运动控制按钮 (例如点动、轴动、程序运行等)。
    - `DobotParameterConfig.js`:  参数配置表单 (例如速度、加速度、力矩等)。
- **状态管理:**  使用 React Context 或 Zustand 管理控制面板的状态，例如机器人连接状态、当前控制模式、参数配置等。
- **API 交互:**  调用后端 API 获取机器人状态数据、发送控制指令。

**后端开发内容 (Flask, Python):**

- **模块文件:** 在 `src/app` 下创建 `src/app/dobot_control_module.py` 文件。
- **API 接口:**
    - `/api/dobot/status`:  GET 请求，返回机器人实时状态 (JSON 格式)。
    - `/api/dobot/connect`:  POST 请求，连接机器人。
    - `/api/dobot/disconnect`:  POST 请求，断开机器人连接。
    - `/api/dobot/move_joint`:  POST 请求，关节运动控制指令。
    - `/api/dobot/move_linear`:  POST 请求，直线运动控制指令。
    - `/api/dobot/set_parameter`:  POST 请求，设置机器人参数。
- **业务逻辑:**
    - 实现与 Dobot 机器人控制器的通信逻辑 (例如使用 Dobot 官方 SDK 或 Modbus TCP 协议)。
    - 处理前端 API 请求，调用机器人控制接口，返回结果。
    - 可以使用 Celery 异步处理一些耗时的控制指令。

### 示例模块 2: **程序可视化编辑器增强**

**功能描述:**  增强现有的流程图编辑器，添加新的节点类型，例如逻辑判断节点、循环节点、数据处理节点等。提升编辑器的易用性和功能性。

**前端开发内容 (Next.js, React):**

- **模块目录:**  扩展 `src/lib/myblockly` 或在 `src/lib` 下创建新的编辑器增强模块目录 (例如 `src/lib/flowchart_editor_enhancements`)。
- **节点扩展:**
    - 创建新的 React 组件，作为新的节点类型 (例如 `LogicNode.js`, `LoopNode.js`, `DataProcessNode.js`)。
    - 在编辑器中注册新的节点类型，并定义其属性、参数和交互逻辑。
    - 可以使用 React Flow 的自定义节点功能来实现。
- **编辑器功能增强:**
    - 添加节点分组和分类功能，方便用户查找和使用节点。
    - 优化节点连接和布局算法，提升编辑器的用户体验。
    - 可以考虑集成代码预览功能 (如 Monaco Editor)，实时显示流程图生成的代码。

**后端开发内容 (Flask, Python):**

- **节点类型定义扩展:**
    - 扩展后端工作流引擎的节点类型注册表 (`node_types.yaml` 或类似文件)。
    - 定义新的节点类型，包括其参数、API 绑定、代码生成模板等。
- **代码生成逻辑增强:**
    - 修改代码生成模块，使其能够处理新的节点类型，生成相应的代码。
    - 优化代码生成模板，提升生成代码的质量和效率。

## 总结

本方案在之前的版本基础上，增加了 **“具体模块开发内容示例”** 章节，更详细地描述了如何进行模块化开发，并提供了两个示例模块的具体开发内容。希望这些更具体的描述能够帮助您更好地理解和实施增量开发方案。

---

请您再次审阅更新后的方案，如果您还有其他问题或需要更详细的内容，请随时提出。