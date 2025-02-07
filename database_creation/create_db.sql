-- 扩展类型，如果你的PostgreSQL版本低于9.4，可能需要先创建 uuid-ossp 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- flowcharts 表
CREATE TABLE flowcharts (
    flowchart_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    flowchart_name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- nodes 表
CREATE TABLE nodes (
    node_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    flowchart_id UUID NOT NULL REFERENCES flowcharts(flowchart_id) ON DELETE CASCADE,
    node_type VARCHAR(50) NOT NULL,
    api_name VARCHAR(100) NOT NULL,
    parameters JSONB,
    description TEXT,
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- edges 表
CREATE TABLE edges (
    edge_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    flowchart_id UUID NOT NULL REFERENCES flowcharts(flowchart_id) ON DELETE CASCADE,
    source_node_id UUID NOT NULL REFERENCES nodes(node_id) ON DELETE CASCADE,
    target_node_id UUID NOT NULL REFERENCES nodes(node_id) ON DELETE CASCADE,
    edge_type VARCHAR(50) DEFAULT 'sequential',
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- dialogue_sessions 表
CREATE TABLE dialogue_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    flowchart_id UUID REFERENCES flowcharts(flowchart_id) ON DELETE CASCADE,
    user_id UUID, -- 可选，如果需要跟踪用户
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    session_status VARCHAR(50) DEFAULT 'ongoing'
);

-- dialogue_messages 表
CREATE TABLE dialogue_messages (
    message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES dialogue_sessions(session_id) ON DELETE CASCADE,
    message_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    message_role VARCHAR(50) NOT NULL, -- 'user' 或 'system' (LLM)
    message_content TEXT NOT NULL
);

-- flowchart_versions 表
CREATE TABLE flowchart_versions (
    version_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    flowchart_id UUID NOT NULL REFERENCES flowcharts(flowchart_id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL, -- 版本号，例如 1, 2, 3...
    version_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    flowchart_data JSONB NOT NULL,
    version_description TEXT
);

-- 初始化数据 (可选，例如创建一些初始流程图或节点类型)
-- 示例：创建一个初始流程图
INSERT INTO flowcharts (flowchart_name, description) VALUES ('Initial Flowchart', 'A basic example flowchart');

-- 示例：创建一些节点类型 (这部分数据可以根据您的节点类型定义来初始化)
-- INSERT INTO node_types (type_name, description) VALUES ('MotionNode', 'Nodes for robot motion control');
-- INSERT INTO node_types (type_name, description) VALUES ('IONode', 'Nodes for IO control');