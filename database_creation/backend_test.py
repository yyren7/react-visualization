import uuid
import datetime
import json
import graphviz # 需要安装 graphviz 库: pip install graphviz

class Node:
    def __init__(self, node_id=None, node_type=None, api_name=None, parameters=None, description=None, position_x=0, position_y=0):
        self.node_id = node_id if node_id else uuid.uuid4()
        self.node_type = node_type
        self.api_name = api_name
        self.parameters = parameters if parameters is not None else {}
        self.description = description
        self.position_x = position_x
        self.position_y = position_y

    def to_dict(self):
        return {
            'node_id': str(self.node_id),
            'node_type': self.node_type,
            'api_name': self.api_name,
            'parameters': self.parameters,
            'description': self.description,
            'position_x': self.position_x,
            'position_y': self.position_y
        }

    @staticmethod
    def from_dict(data):
        return Node(
            node_id=uuid.UUID(data['node_id']),
            node_type=data['node_type'],
            api_name=data['api_name'],
            parameters=data['parameters'],
            description=data['description'],
            position_x=data['position_x'],
            position_y=data['position_y']
        )

class Edge:
    def __init__(self, edge_id=None, source_node_id=None, target_node_id=None, edge_type='sequential', description=None, condition=None, edge_label=None):
        self.edge_id = edge_id if edge_id else uuid.uuid4()
        self.source_node_id = source_node_id
        self.target_node_id = target_node_id
        self.edge_type = edge_type
        self.description = description
        self.condition = condition
        self.edge_label = edge_label

    def to_dict(self):
        return {
            'edge_id': str(self.edge_id),
            'source_node_id': str(self.source_node_id),
            'target_node_id': str(self.target_node_id),
            'edge_type': self.edge_type,
            'description': self.description,
            'condition': self.condition,
            'edge_label': self.edge_label
        }

    @staticmethod
    def from_dict(data):
        return Edge(
            edge_id=uuid.UUID(data['edge_id']),
            source_node_id=uuid.UUID(data['source_node_id']),
            target_node_id=uuid.UUID(data['target_node_id']),
            edge_type=data['edge_type'],
            description=data['description'],
            condition=data.get('condition'),
            edge_label=data.get('edge_label')
        )

class Flowchart:
    def __init__(self, flowchart_id=None, flowchart_name=None, nodes=None, edges=None, description=None, global_parameters=None): # 添加 global_parameters
        self.flowchart_id = flowchart_id if flowchart_id else uuid.uuid4()
        self.flowchart_name = flowchart_name
        self.nodes = nodes if nodes is not None else []
        self.edges = edges if edges is not None else []
        self.description = description
        self.global_parameters = global_parameters if global_parameters is not None else {} # 初始化 global_parameters

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)

    def to_dict(self):
        return {
            'flowchart_id': str(self.flowchart_id),
            'flowchart_name': self.flowchart_name,
            'nodes': [node.to_dict() for node in self.nodes],
            'edges': [edge.to_dict() for edge in self.edges],
            'description': self.description,
            'global_parameters': self.global_parameters # 添加 global_parameters 到 to_dict
        }

    @staticmethod
    def from_dict(data):
        flowchart = Flowchart(
            flowchart_id=uuid.UUID(data['flowchart_id']),
            flowchart_name=data['flowchart_name'],
            description=data['description'],
            global_parameters=data.get('global_parameters') # 从 dict 加载 global_parameters
        )
        flowchart.nodes = [Node.from_dict(node_data) for node_data in data['nodes']]
        flowchart.edges = [Edge.from_dict(edge_data) for edge_data in data['edges']]
        return flowchart

    def save_version(self, version_number, version_description=None, db_connection=None):
        """保存当前流程图版本到数据库."""
        version_id = uuid.uuid4()
        flowchart_data_json = json.dumps(self.to_dict()) # 将 Flowchart 对象转换为 JSON 字符串

        if db_connection: # 假设您有一个数据库连接对象 db_connection
            cursor = db_connection.cursor()
            cursor.execute(
                """
                INSERT INTO flowchart_versions (version_id, flowchart_id, version_number, version_time, flowchart_data, version_description)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s)
                """,
                (version_id, self.flowchart_id, version_number, datetime.datetime.now(datetime.timezone.utc), flowchart_data_json, version_description)
            )
            db_connection.commit()
            cursor.close()
        else:
            print("Warning: Database connection not provided, version not saved to DB.")

    @staticmethod
    def load_version(version_id, db_connection):
        """从数据库加载指定版本的流程图."""
        if db_connection:
            cursor = db_connection.cursor()
            cursor.execute(
                "SELECT flowchart_data FROM flowchart_versions WHERE version_id = %s",
                (version_id,)
            )
            result = cursor.fetchone()
            cursor.close()
            if result:
                flowchart_data = json.loads(result[0]) # 从 JSON 字符串反序列化为字典
                return Flowchart.from_dict(flowchart_data) # 从字典创建 Flowchart 对象
            else:
                return None
        else:
            print("Error: Database connection not provided.")
            return None
        
    def __init__(self, flowchart_id=None, flowchart_name=None, nodes=None, edges=None, description=None):
        self.flowchart_id = flowchart_id if flowchart_id else uuid.uuid4()
        self.flowchart_name = flowchart_name
        self.nodes = nodes if nodes is not None else []
        self.edges = edges if edges is not None else []
        self.description = description

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)

    def to_dict(self):
        return {
            'flowchart_id': str(self.flowchart_id),
            'flowchart_name': self.flowchart_name,
            'nodes': [node.to_dict() for node in self.nodes],
            'edges': [edge.to_dict() for edge in self.edges],
            'description': self.description
        }

    @staticmethod
    def from_dict(data):
        flowchart = Flowchart(
            flowchart_id=uuid.UUID(data['flowchart_id']),
            flowchart_name=data['flowchart_name'],
            description=data['description']
        )
        flowchart.nodes = [Node.from_dict(node_data) for node_data in data['nodes']]
        flowchart.edges = [Edge.from_dict(edge_data) for edge_data in data['edges']]
        return flowchart

    def save_version(self, version_number, version_description=None, db_connection=None):
        """保存当前流程图版本到数据库."""
        version_id = uuid.uuid4()
        flowchart_data_json = json.dumps(self.to_dict()) # 将 Flowchart 对象转换为 JSON 字符串

        if db_connection: # 假设您有一个数据库连接对象 db_connection
            cursor = db_connection.cursor()
            cursor.execute(
                """
                INSERT INTO flowchart_versions (version_id, flowchart_id, version_number, version_time, flowchart_data, version_description)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s)
                """,
                (version_id, self.flowchart_id, version_number, datetime.datetime.now(datetime.timezone.utc), flowchart_data_json, version_description)
            )
            db_connection.commit()
            cursor.close()
        else:
            print("Warning: Database connection not provided, version not saved to DB.")

    @staticmethod
    def load_version(version_id, db_connection):
        """从数据库加载指定版本的流程图."""
        if db_connection:
            cursor = db_connection.cursor()
            cursor.execute(
                "SELECT flowchart_data FROM flowchart_versions WHERE version_id = %s",
                (version_id,)
            )
            result = cursor.fetchone()
            cursor.close()
            if result:
                flowchart_data = json.loads(result[0]) # 从 JSON 字符串反序列化为字典
                return Flowchart.from_dict(flowchart_data) # 从字典创建 Flowchart 对象
            else:
                return None
        else:
            print("Error: Database connection not provided.")
            return None

class DialogueSession:
    def __init__(self, session_id=None, flowchart_id=None, user_id=None, start_time=None, end_time=None, session_status='ongoing'):
        self.session_id = session_id if session_id else uuid.uuid4()
        self.flowchart_id = flowchart_id
        self.user_id = user_id
        self.start_time = start_time if start_time else datetime.datetime.now(datetime.timezone.utc)
        self.end_time = end_time
        self.session_status = session_status
        self.messages = [] # 存储 DialogueMessage 对象列表

    def add_message(self, role, content):
        message = DialogueMessage(session_id=self.session_id, role=role, content=content)
        self.messages.append(message)
        return message

    def complete_session(self, flowchart_id):
        self.flowchart_id = flowchart_id
        self.end_time = datetime.datetime.now(datetime.timezone.utc)
        self.session_status = 'completed'

    def save_to_db(self, db_connection):
        """保存会话信息和所有消息到数据库."""
        if db_connection:
            try:
                cursor = db_connection.cursor()
                # 保存 dialogue_sessions 表
                cursor.execute(
                    """
                    INSERT INTO dialogue_sessions (session_id, flowchart_id, user_id, start_time, end_time, session_status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (session_id) DO UPDATE
                    SET flowchart_id = EXCLUDED.flowchart_id,
                        user_id = EXCLUDED.user_id,
                        start_time = EXCLUDED.start_time,
                        end_time = EXCLUDED.end_time,
                        session_status = EXCLUDED.session_status;
                    """,
                    (self.session_id, self.flowchart_id, self.user_id, self.start_time, self.end_time, self.session_status)
                )
                # 保存 dialogue_messages 表
                for message in self.messages:
                    message.save_to_db(db_connection)
                db_connection.commit()
                cursor.close()
            except Exception as e:
                db_connection.rollback()
                print(f"Error saving dialogue session to database: {e}")
        else:
            print("Error: Database connection not provided.")

    @staticmethod
    def load_from_db(session_id, db_connection):
        """从数据库加载对话会话和所有消息."""
        if db_connection:
            try:
                cursor = db_connection.cursor()
                # 加载 dialogue_sessions 表
                cursor.execute(
                    "SELECT flowchart_id, user_id, start_time, end_time, session_status FROM dialogue_sessions WHERE session_id = %s",
                    (session_id,)
                )
                session_data = cursor.fetchone()
                if not session_data:
                    return None # Session not found

                session = DialogueSession(
                    session_id=session_id,
                    flowchart_id=session_data[0],
                    user_id=session_data[1],
                    start_time=session_data[2],
                    end_time=session_data[3],
                    session_status=session_data[4]
                )
                # 加载 dialogue_messages 表
                cursor.execute(
                    "SELECT message_id, message_time, message_role, message_content FROM dialogue_messages WHERE session_id = %s ORDER BY message_time ASC",
                    (session_id,)
                )
                message_records = cursor.fetchall()
                for record in message_records:
                    message = DialogueMessage(
                        message_id=record[0],
                        session_id=session_id,
                        message_time=record[1],
                        role=record[2],
                        content=record[3]
                    )
                    session.messages.append(message)
                cursor.close()
                return session
            except Exception as e:
                print(f"Error loading dialogue session from database: {e}")
                return None
        else:
            print("Error: Database connection not provided.")
            return None


class DialogueMessage:
    def __init__(self, message_id=None, session_id=None, message_time=None, role=None, content=None):
        self.message_id = message_id if message_id else uuid.uuid4()
        self.session_id = session_id
        self.message_time = message_time if message_time else datetime.datetime.now(datetime.timezone.utc)
        self.role = role
        self.content = content

    def save_to_db(self, db_connection):
        """保存消息到数据库."""
        if db_connection:
            try:
                cursor = db_connection.cursor()
                cursor.execute(
                    """
                    INSERT INTO dialogue_messages (message_id, session_id, message_time, message_role, message_content)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (message_id) DO UPDATE
                    SET session_id = EXCLUDED.session_id,
                        message_time = EXCLUDED.message_time,
                        message_role = EXCLUDED.message_role,
                        message_content = EXCLUDED.message_content;
                    """,
                    (self.message_id, self.session_id, self.message_time, self.role, self.content)
                )
                cursor.close()
            except Exception as e:
                print(f"Error saving dialogue message to database: {e}")
        else:
            print("Error: Database connection not provided.")
            
def create_pick_place_loop_flowchart():
    flowchart = Flowchart(flowchart_name="Pick and Place Loop", description="Simple pick and place task with loop")

    # Define positions (replace with actual positions)
    pos1 = {"X": 200, "Y": 0, "Z": 100, "R": 0}
    pos2 = {"X": 0, "Y": 200, "Z": 100, "R": 0}
    loop_iterations = 3 # Example loop iterations

    # 1. Initialize Robot (EnableRobot)
    init_robot_node = Node(node_type="ControlNode", api_name="EnableRobot", description="Enable Robot")
    flowchart.add_node(init_robot_node)

    # 2. Loop Start Node
    loop_start_node = Node(node_type="LoopStartNode", description=f"Loop Start ({loop_iterations} iterations)", parameters={'loop_type': 'CountLoop', 'iterations': loop_iterations, 'counter_variable_name': 'loop_count'})
    flowchart.add_node(loop_start_node)

    # 3. Move to Position 1 (MovJ)
    move_to_pos1_node = Node(node_type="MotionNode", api_name="MovJ", parameters=pos1, description="Move to Position 1")
    flowchart.add_node(move_to_pos1_node)

    # 4. Close Gripper (ToolDOExecute)
    close_gripper_node = Node(node_type="IONode", api_name="ToolDOExecute", parameters={'index': 1, 'status': 1}, description="Close Gripper")
    flowchart.add_node(close_gripper_node)

    # 5. Move to Position 2 (MovJ)
    move_to_pos2_node = Node(node_type="MotionNode", api_name="MovJ", parameters=pos2, description="Move to Position 2")
    flowchart.add_node(move_to_pos2_node)

    # 6. Open Gripper (ToolDOExecute)
    open_gripper_node = Node(node_type="IONode", api_name="ToolDOExecute", parameters={'index': 1, 'status': 0}, description="Open Gripper")
    flowchart.add_node(open_gripper_node)

    # 7. Loop End Node
    loop_end_node = Node(node_type="LoopEndNode", description="Loop End")
    flowchart.add_node(loop_end_node)

    # 8. Disable Robot (DisableRobot)
    disable_robot_node = Node(node_type="ControlNode", api_name="DisableRobot", description="Disable Robot")
    flowchart.add_node(disable_robot_node)

    # Define Edges
    flowchart.add_edge(Edge(source_node_id=init_robot_node.node_id, target_node_id=loop_start_node.node_id)) # 1 -> 2
    flowchart.add_edge(Edge(source_node_id=loop_start_node.node_id, target_node_id=move_to_pos1_node.node_id)) # 2 -> 3 (Enter Loop)
    flowchart.add_edge(Edge(source_node_id=move_to_pos1_node.node_id, target_node_id=close_gripper_node.node_id)) # 3 -> 4
    flowchart.add_edge(Edge(source_node_id=close_gripper_node.node_id, target_node_id=move_to_pos2_node.node_id)) # 4 -> 5
    flowchart.add_edge(Edge(source_node_id=move_to_pos2_node.node_id, target_node_id=open_gripper_node.node_id)) # 5 -> 6
    flowchart.add_edge(Edge(source_node_id=open_gripper_node.node_id, target_node_id=loop_end_node.node_id)) # 6 -> 7 (Loop Body End)
    flowchart.add_edge(Edge(source_node_id=loop_end_node.node_id, target_node_id=loop_start_node.node_id, edge_type='loop_back', condition=f'loop_count < {loop_iterations}', edge_label='Loop')) # 7 -> 2 (Loop Back)
    flowchart.add_edge(Edge(source_node_id=loop_end_node.node_id, target_node_id=disable_robot_node.node_id, edge_label='End Loop')) # 7 -> 8 (Exit Loop)


    return flowchart

def get_flowchart_json(flowchart):
    return json.dumps(flowchart.to_dict(), indent=4)

def visualize_flowchart_graphviz(flowchart, filename="flowchart_visualization"):
    dot = graphviz.Digraph(comment='Robot Task Flowchart', format='png', graph_attr={'rankdir': 'TB'}) # TB for top-to-bottom layout

    node_map = {node.node_id: node for node in flowchart.nodes} # For easy node lookup

    for node in flowchart.nodes:
        label = f"{node.node_type}\n{node.api_name if node.api_name else ''}\n{node.description if node.description else ''}"
        params_str = "\n".join([f"{k}: {v}" for k, v in node.parameters.items()]) if node.parameters else ""
        if params_str:
            label += "\nParameters:\n" + params_str

        dot.node(str(node.node_id), label=label, shape='box') # Use box shape for nodes

    for edge in flowchart.edges:
        label = edge.edge_label if edge.edge_label else ""
        if edge.condition:
            label += f"\nCondition: {edge.condition}"
        dot.edge(str(edge.source_node_id), str(edge.target_node_id), label=label)

    dot.render(filename, view=False) # view=True will open the image viewer

# --- Main execution ---
if __name__ == "__main__":
    flowchart = create_pick_place_loop_flowchart()
    flowchart_json = get_flowchart_json(flowchart)
    print("Flowchart JSON:\n", flowchart_json)

    visualize_flowchart_graphviz(flowchart)
    print(f"Flowchart visualization saved to flowchart_visualization.png")