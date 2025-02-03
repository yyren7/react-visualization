import plotly.graph_objects as go
from ipywidgets import interact, FloatSlider
import ipywidgets as widgets
from IPython.display import display, HTML


# ====================
# 阶段1：结构化输入模板
# ====================
def create_phase1():
    fig = go.Figure()

    # 模板结构
    template = {
        "process": [
            {"action": "启动机器人", "params": {"speed": 50}},
            {"action": "平移操作", "params": {"x": 100, "y": 200}},
            {"action": "夹具操作", "params": {"state": "开启"}}
        ]
    }

    # 可视化模板
    fig.add_trace(go.Table(
        header=dict(values=["步骤", "参数"], fill_color="#1f77b4", font=dict(color="white")),
        cells=dict(values=[
            [step["action"] for step in template["process"]],
            [str(step["params"]) for step in template["process"]]
        ])
    ))

    fig.update_layout(
        title="Phase 1: 结构化需求输入模板",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


# ====================
# 阶段2：流程图编辑器
# ====================
def create_flowchart(x=100, y=200, speed=50):
    fig = go.Figure()

    # 节点定义
    nodes = [
        dict(type="circle", xref="x", yref="y",
             x0=0.1, y0=0.7, x1=0.3, y1=0.9, line=dict(width=2)),
        dict(type="rect", x0=0.4, y0=0.6, x1=0.6, y1=0.8,
             line=dict(width=2), label="平移操作"),
        dict(type="circle", xref="x", yref="y",
             x0=0.7, y0=0.7, x1=0.9, y1=0.9, line=dict(width=2))
    ]

    # 连接线
    fig.add_trace(go.Scatter(
        x=[0.2, 0.4, 0.6, 0.8],
        y=[0.8, 0.7, 0.7, 0.8],
        mode="lines+markers",
        line=dict(color="#2ca02c", width=3)
    ))

    # 参数标注
    fig.add_annotation(
        x=0.5, y=0.5,
        text=f"<b>当前参数</b><br>X: {x}mm<br>Y: {y}mm<br>速度: {speed}%",
        showarrow=False,
        bordercolor="#1f77b4",
        bgcolor="white"
    )

    fig.update_layout(
        shapes=nodes,
        title="Phase 2: 可视化流程编辑",
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        margin=dict(l=20, r=20, t=40, b=20),
        height=500
    )
    return fig


# ====================
# 阶段3：代码生成器
# ====================
def generate_code(x=100, y=200, speed=50):
    code = f"""def robot_program():
    # Auto-generated Code
    start_robot(speed={speed})
    move_to(x={x}, y={y})
    set_gripper(state=True)
    stop_robot()"""
    return f"<pre style='background:#f8f9fa;padding:20px'>{code}</pre>"


# ====================
# 交互式界面
# ====================
@interact(
    x=FloatSlider(min=0, max=300, value=100, description="X坐标"),
    y=FloatSlider(min=0, max=300, value=200, description="Y坐标"),
    speed=FloatSlider(min=0, max=100, value=50, description="速度%")
)
def update_interface(x, y, speed):
    # 显示阶段1
    phase1 = create_phase1()
    phase1.show()

    # 显示阶段2
    phase2 = create_flowchart(x, y, speed)
    phase2.show()

    # 显示阶段3
    display(HTML("<h4>Phase 3: 可执行代码生成</h4>"))
    display(HTML(generate_code(x, y, speed)))


# 首次运行
