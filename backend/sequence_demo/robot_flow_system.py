import os
from typing import List, Dict, Any
from langgraph.graph import END, StateGraph
from langchain_core.messages import HumanMessage
from langchain_community.chat_models import ChatOpenAI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import redis
import threading
import time
from neo4j import GraphDatabase, basic_auth


# ================= 配置部分 =================
class Config:
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "yyren"
    NEO4J_PASSWORD = "yyren123123"
    REDIS_URL = "redis://localhost:6379/0"
    OLLAMA_ENDPOINT = "http://192.168.16.119:11434/v1"


config = Config()

# ============== Neo4j数据库初始化 ==============
try:
    driver = GraphDatabase.driver(
        config.NEO4J_URI,
        auth=basic_auth(config.NEO4J_USER, config.NEO4J_PASSWORD)
    )
    driver.verify_connectivity()
except Exception as e:
    print(f"Neo4j连接失败: {e}")
    exit(1)

redis_client = redis.Redis.from_url(config.REDIS_URL)

# ============== 本地LLM客户端 ==============
local_llm = ChatOpenAI(
    model="hf.co/bartowski/DeepSeek-R1-Distill-Qwen-32B-GGUF:Q5_K_S",
    base_url=config.OLLAMA_ENDPOINT,
    api_key='ollama'
)


# ============== LangGraph流程定义 ==============
class GraphState(BaseModel):
    user_input: str
    current_graph: Dict[str, Any] = None
    validation_errors: List[str] = []
    generated_operations: List[Dict] = []


def parse_input(state: GraphState):
    """使用LLM解析自然语言指令"""
    message = local_llm.invoke([
        HumanMessage(content=f"""
        请将以下用户需求转换为图操作指令：
        用户输入：{state.user_input}
        可用节点类型：RobotAction, CollaborationEdge
        输出格式：JSON {{"operations": [{{"type": "add/node", "data": {{...}}}}, ...]}}
        """)
    ])
    try:
        operations = json.loads(message.content)["operations"]
        return {"generated_operations": operations}
    except:
        return {"validation_errors": ["LLM返回格式错误"]}


def validate_operations(state: GraphState):
    """验证图操作合法性"""
    errors = []
    for op in state.generated_operations:
        if op["type"] == "add/node":
            if "name" not in op["data"]:
                errors.append(f"节点缺少name字段: {op}")
        elif op["type"] == "add/edge":
            if "sources" not in op["data"]:
                errors.append(f"边缺少sources字段: {op}")
    return {"validation_errors": errors}


def apply_operations(state: GraphState):
    """应用操作到Neo4j数据库"""
    if not state.validation_errors:
        with driver.session() as session:
            for op in state.generated_operations:
                if op["type"] == "add/node":
                    session.run(
                        "CREATE (n:RobotAction {id: $id, name: $name, params: $params, session_id: $session_id})",
                        id=op["data"]["id"],
                        name=op["data"]["name"],
                        params=json.dumps(op["data"]["params"]),
                        session_id=op["data"]["session_id"]
                    )
                elif op["type"] == "add/edge":
                    session.run(
                        """
                        MATCH (a:RobotAction), (b:RobotAction)
                        WHERE a.id = $source_id AND b.id = $target_id
                        CREATE (a)-[r:CollaborationEdge {id: $id, robots: $robots, constraints: $constraints}]->(b)
                        """,
                        source_id=op["data"]["sources"][0],
                        target_id=op["data"]["targets"][0],
                        id=op["data"]["id"],
                        robots=op["data"]["params"]["robots"],
                        constraints=json.dumps(op["data"]["params"]["constraints"])
                    )
        redis_client.delete("graph_cache")
    return state


workflow = StateGraph(GraphState)
workflow.add_node("parse_input", parse_input)
workflow.add_node("validate", validate_operations)
workflow.add_node("apply", apply_operations)

workflow.set_entry_point("parse_input")
workflow.add_edge("parse_input", "validate")
workflow.add_conditional_edges(
    "validate",
    lambda state: END if state.validation_errors else "apply",
    {"apply": "apply", END: END}
)
langchain_app = workflow.compile()

# ============== FastAPI接口 ==============
app = FastAPI()


class UserRequest(BaseModel):
    text: str
    session_id: str


@app.post("/process_command")
async def process_command(request: UserRequest):
    """处理自然语言指令"""
    state = GraphState(user_input=request.text)
    result = await langchain_app.ainvoke(state)

    # 获取更新后的图
    updated_graph = get_subgraph(request.session_id)

    # 生成可执行代码
    code = generate_robot_code(updated_graph)

    return {
        "graph": updated_graph,
        "code": code,
        "errors": result.validation_errors
    }


# ============== 图操作工具函数 ==============
def get_subgraph(session_id: str):
    """获取带缓存的子图"""
    cache_key = f"subgraph_{session_id}"
    if redis_client.exists(cache_key):
        return json.loads(redis_client.get(cache_key))

    with driver.session() as session:
        result = session.run(
            """
            MATCH (n:RobotAction)-[e:CollaborationEdge*3]->(m:RobotAction)
            WHERE n.session_id = $session_id
            RETURN n, e, m
            LIMIT 100
            """,
            session_id=session_id
        )
        subgraph = {"nodes": [], "edges": []}
        for record in result:
            subgraph["nodes"].append(record["n"])
            subgraph["edges"].append(record["e"])
        redis_client.setex(cache_key, 300, json.dumps(subgraph))
    return subgraph


# ============== 代码生成引擎 ==============
def generate_robot_code(hypergraph: Dict) -> str:
    code = []
    sync_groups = {}

    # 解析边生成同步点
    for edge in hypergraph.get("edges", []):
        if edge["type"] == "CollaborationEdge":
            sync_id = f"sync_{abs(hash(edge))}"
            robots = edge["params"]["robots"]
            code.append(f"# 协作组 {', '.join(robots)}")
            code.append(f"with RobotSync({robots}) as {sync_id}:")
            code.append(f"    set_constraints({edge['params']['constraints']})")
            sync_groups[edge["id"]] = sync_id

    # 生成节点代码
    for node in hypergraph.get("nodes", []):
        if node["type"] == "RobotAction":
            params = node.get("params", {})
            safe_params = apply_safety_limits(params)
            code.append(f"{node['name']}(**{safe_params})")

            # 添加同步等待
            for edge_id in node.get("edges", []):
                if edge_id in sync_groups:
                    code.append(f"{sync_groups[edge_id]}.wait()")

    return "\n".join(code)


def apply_safety_limits(params: Dict) -> Dict:
    """应用安全限制"""
    limited = params.copy()
    if "speed" in params:
        limited["speed"] = min(params["speed"], 1.0)  # 最大速度限制
    if "force" in params:
        limited["force"] = min(params["force"], 150)  # 最大力限制
    return limited


# ============== 启动系统 ==============
if __name__ == "__main__":

    # 启动FastAPI服务
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)