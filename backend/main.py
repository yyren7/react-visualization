import os
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis
import json
import uuid
from neo4j import GraphDatabase, basic_auth
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage


# 配置调整为本地环境
class Config:
    # 确保本地Neo4j已启动并修改为你的实际配置
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "yyren"
    NEO4J_PASSWORD = "yyren123123"  # 修改为你的Neo4j密码

    # 确保本地Redis已安装并运行
    REDIS_URL = "redis://localhost:6379/0"

    # 确保Ollama服务在本地运行
    OLLAMA_ENDPOINT = "http://localhost:11434/v1"  # 使用localhost替代IP


config = Config()

# 初始化Neo4j驱动（添加错误处理）
try:
    driver = GraphDatabase.driver(
        config.NEO4J_URI,
        auth=basic_auth(config.NEO4J_USER, config.NEO4J_PASSWORD)
    )
    driver.verify_connectivity()
except Exception as e:
    print(f"Neo4j连接失败: {e}")
    exit(1)

# 初始化Redis连接
redis_client = redis.Redis.from_url(config.REDIS_URL)


# 添加内存数据库模拟（用于示例）
class MemoryDB:
    def init(self):
        self.nodes = {}
        self.edges = {}


def add(self, node):
    self.nodes[node.id] = node


def get(self, node_id):
    return self.nodes.get(node_id)


def link(self, edge, nodes):
    self.edges[edge.id] = {"edge": edge, "nodes": nodes}


db = MemoryDB()  # 替换为实际数据库操作

# 定义数据模型
class RobotAction(BaseModel):
    id: str
    name: str
    params: dict
    session_id: str

class CollaborationEdge(BaseModel):
    id: str
    source_id: str
    target_id: str
    robots: List[str]
    constraints: Dict

# FastAPI应用
app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# LangGraph状态机
class GraphState(BaseModel):
    user_input: str
    current_graph: Dict = None
    validation_errors: List[str] = []
    generated_operations: List[Dict] = []


local_llm = ChatOpenAI(
    model="hf.co/bartowski/DeepSeek-R1-Distill-Qwen-32B-GGUF:Q5_K_S",
    base_url=config.OLLAMA_ENDPOINT,
    api_key='ollama'
)


def parse_input(state: GraphState):
    prompt = f"""将用户指令转换为超图操作：
    输入：{state.user_input}
    输出格式：{{"operations": [{{"type": "add/node", "data": {{...}}}}, ...]}}"""

    res = local_llm.invoke([HumanMessage(content=prompt)])
    try:
        return {"generated_operations": json.loads(res.content)["operations"]}
    except:
        return {"validation_errors": ["解析失败"]}


def validate_operations(state: GraphState):
    errors = []
    for op in state.generated_operations:
        if op["type"] == "add/node" and "name" not in op["data"]:
            errors.append(f"节点缺少名称: {op}")
        elif op["type"] == "add/edge" and "sources" not in op["data"]:
            errors.append(f"超边缺少源节点: {op}")
    return {"validation_errors": errors}


def apply_operations(state: GraphState):
    if not state.validation_errors:
        for op in state.generated_operations:
            if op["type"] == "add/node":
                node = RobotAction(**op["data"])
                db.add(node)
            elif op["type"] == "add/edge":
                sources = [db.get(id) for id in op["data"]["sources"]]
                targets = [db.get(id) for id in op["data"]["targets"]]
                edge = CollaborationEdge(**op["data"]["params"])
                db.link(edge, sources + targets)
        redis_client.delete("graph_cache")
    return state


workflow = StateGraph(GraphState)
workflow.add_node("parse", parse_input)
workflow.add_node("validate", validate_operations)
workflow.add_node("apply", apply_operations)
workflow.set_entry_point("parse")
workflow.add_edge("parse", "validate")
workflow.add_conditional_edges(
    "validate",
    lambda s: END if s.validation_errors else "apply",
    {"apply": "apply", END: END}
)
langchain_chain = workflow.compile()


# API接口
class UserRequest(BaseModel):
    text: str
    session_id: str


@app.post("/process_command")
async def process_command(request: UserRequest):
    state = GraphState(user_input=request.text)
    result = await langchain_chain.ainvoke(state)
    return {
        "graph": get_subgraph(request.session_id),
        "code": generate_code(result.current_graph),
        "errors": result.validation_errors
    }


@app.post("/api/nodes")
async def create_node(data: dict):
    new_node = RobotAction(name="新动作", params={})
    db.add(new_node)
    return {"id": new_node.id, "position": data.get("position", [0, 0])}


@app.put("/api/nodes/{node_id}")
async def update_node(node_id: str, data: dict):
    node = db.get(node_id)
    if not node: raise HTTPException(404, "节点不存在")

    if 'speed' in data and data['speed'] > 1.0:
        raise HTTPException(400, "速度超过安全限制")

    node.name = data.get("name", node.name)
    node.params = data.get("params", node.params)
    db.update(node)
    return {"status": "updated"}


@app.post("/api/edges")
async def create_edge(data: dict):
    source = db.get(data['source'])
    target = db.get(data['target'])
    if not source or not target:
        raise HTTPException(400, "节点不存在")

    edge = CollaborationEdge(robots=[], constraints={})
    db.link(edge, [source, target])
    return {"id": edge.id}


@app.post("/api/delete")
async def delete_elements(data: dict):
    for item in data["elements"]:
        if item["type"] == "node":
            db.delete_node(item["id"])
        elif item["type"] == "edge":
            db.delete_edge(item["id"])
    return {"status": "success"}


# 工具函数
def get_subgraph(session_id: str):
    cache_key = f"subgraph_{session_id}"
    if cached := redis_client.get(cache_key):
        return json.loads(cached)

    subgraph = {
        "nodes": [n.__dict__ for n in db.query("MATCH (n) WHERE n.session_id = $sid RETURN n", sid=session_id)],
        "edges": [e.__dict__ for e in db.query("MATCH ()-[e]->() RETURN e")]
    }
    redis_client.setex(cache_key, 300, json.dumps(subgraph))
    return subgraph


def generate_code(graph: Dict) -> str:
    code = []
    sync_points = {}

    for edge in graph.get("edges", []):
        if edge["type"] == "CollaborationEdge":
            sync_id = f"sync_{abs(hash(edge))}"
            code.append(f"with RobotSync({edge['robots']}) as {sync_id}:")
            code.append(f"    set_constraints({edge['constraints']})")
            sync_points[edge['id']] = sync_id

    for node in graph.get("nodes", []):
        if node["type"] == "RobotAction":
            params = {k: min(v, 1.0) if k == 'speed' else v for k, v in node["params"].items()}
            code.append(f"{node['name']}(**{params})")
            for edge_id in node.get("edges", []):
                if edge_id in sync_points:
                    code.append(f"{sync_points[edge_id]}.wait()")

    return "\n".join(code)


# 启动服务（保持不变）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)