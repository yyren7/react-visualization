# 系统核心文件：robot_flow_system.py
import os
from typing import List, Dict, Any
from langgraph.graph import END, StateGraph
from langchain_core.messages import HumanMessage
from langchain_community.chat_models import ChatOpenAI
from hypergraphdb import Hypergraph, Atom
import tensorflow_gnn as tfgnn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import redis
import threading
import time

# ================= 配置部分 =================
class Config:
    HYPERGRAPH_PATH = "./robot_hypergraph"
    REDIS_URL = "redis://localhost:6379/0"
    OLLAMA_ENDPOINT = "http://192.168.16.119:11434/v1"

config = Config()

# ============== 超图数据库初始化 ==============
db = Hypergraph(config.HYPERGRAPH_PATH)
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
        请将以下用户需求转换为超图操作指令：
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
    """验证超图操作合法性"""
    errors = []
    for op in state.generated_operations:
        if op["type"] == "add/node":
            if "name" not in op["data"]:
                errors.append(f"节点缺少name字段: {op}")
        elif op["type"] == "add/edge":
            if "sources" not in op["data"]:
                errors.append(f"超边缺少sources字段: {op}")
    return {"validation_errors": errors}

def apply_operations(state: GraphState):
    """应用操作到超图数据库"""
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
        redis_client.delete("graph_cache")  # 清除缓存
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
    
    # 获取更新后的超图
    updated_graph = get_subgraph(request.session_id)
    
    # 生成可执行代码
    code = generate_robot_code(updated_graph)
    
    return {
        "graph": updated_graph,
        "code": code,
        "errors": result.validation_errors
    }

# ============== 超图操作工具函数 ==============
def get_subgraph(session_id: str):
    """获取带缓存的子图"""
    cache_key = f"subgraph_{session_id}"
    if redis_client.exists(cache_key):
        return json.loads(redis_client.get(cache_key))
    
    # 从数据库查询最近修改的子图
    subgraph = db.query(f"""
        MATCH (n)-[e*3]->(m) 
        WHERE n.session_id = '{session_id}'
        RETURN n, e, m
        LIMIT 100
    """)
    redis_client.setex(cache_key, 300, json.dumps(subgraph))
    return subgraph

# ============== GNN实时优化线程 ==============
class GNNMonitor(threading.Thread):
    def run(self):
        while True:
            try:
                graph_data = get_latest_graph()
                dataset = create_dataset(graph_data)
                predictions = hypergnn.predict(dataset)
                handle_predictions(predictions)
            except Exception as e:
                print(f"GNN监控错误: {str(e)}")
            time.sleep(10)

def handle_predictions(predictions):
    """处理GNN预测结果"""
    high_risk_nodes = [n for n, p in predictions.items() if p > 0.7]
    if high_risk_nodes:
        warnings = {"nodes": high_risk_nodes, "message": "检测到高风险节点"}
        redis_client.publish("risk_warnings", json.dumps(warnings))

# ============== 代码生成引擎 ==============
def generate_robot_code(hypergraph: Dict) -> str:
    code = []
    sync_groups = {}
    
    # 解析超边生成同步点
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
    # 启动GNN监控线程
    GNNMonitor().start()
    
    # 启动FastAPI服务
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
