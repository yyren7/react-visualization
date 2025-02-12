// Improved Database Schema Visualization v15 - Removed flowchart_collaborators table

digraph database_schema_v15 {
    graph [rankdir=TB splines=ortho]

    node [shape=plaintext]

    users [label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
      <TR><TD BGCOLOR="lightblue"><b>users</b></TD></TR>
      <TR><TD ALIGN="LEFT">user_id : UUID (PK)</TD></TR>
      <TR><TD ALIGN="LEFT">username : VARCHAR(255) (UNIQUE, NOT NULL)</TD></TR>
      <TR><TD ALIGN="LEFT">email : VARCHAR(255) (UNIQUE)</TD></TR>
      <TR><TD ALIGN="LEFT">password_hash : VARCHAR(255)</TD></TR>
      <TR><TD ALIGN="LEFT">role : VARCHAR(50) (DEFAULT 'user')</TD></TR>
      <TR><TD ALIGN="LEFT">last_login_at : TIMESTAMP WITH TIME ZONE</TD></TR>
      <TR><TD ALIGN="LEFT">is_active : BOOLEAN (DEFAULT TRUE)</TD></TR>
      <TR><TD ALIGN="LEFT">created_at : TIMESTAMP WITH TIME ZONE</TD></TR>
      <TR><TD ALIGN="LEFT">updated_at : TIMESTAMP WITH TIME ZONE</TD></TR>
    </TABLE>>]

    flowcharts [label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
      <TR><TD BGCOLOR="lightblue"><b>flowcharts</b></TD></TR>
      <TR><TD ALIGN="LEFT">flowchart_id : UUID (PK)</TD></TR>
      <TR><TD ALIGN="LEFT">creator_user_id : UUID (FK to users)</TD></TR>
      <TR><TD ALIGN="LEFT">flowchart_name : VARCHAR(255)</TD></TR>
      <TR><TD ALIGN="LEFT">description : TEXT</TD></TR>
      <TR><TD ALIGN="LEFT">is_public : BOOLEAN (DEFAULT FALSE)</TD></TR>
      <TR><TD ALIGN="LEFT">global_parameters : JSONB</TD></TR>
      <TR><TD ALIGN="LEFT">created_at : TIMESTAMP WITH TIME ZONE</TD></TR>
      <TR><TD ALIGN="LEFT">updated_at : TIMESTAMP WITH TIME ZONE</TD></TR>
    </TABLE>>]

    flowchart_versions [label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
      <TR><TD BGCOLOR="lightblue"><b>flowchart_versions</b></TD></TR>
      <TR><TD ALIGN="LEFT">version_id : UUID (PK)</TD></TR>
      <TR><TD ALIGN="LEFT">flowchart_id : UUID (FK to flowcharts)</TD></TR>
      <TR><TD ALIGN="LEFT">version_number : INTEGER</TD></TR>
      <TR><TD ALIGN="LEFT">nodes_json : JSONB</TD></TR>
      <TR><TD ALIGN="LEFT">edges_json : JSONB</TD></TR>
      <TR><TD ALIGN="LEFT">created_at : TIMESTAMP WITH TIME ZONE</TD></TR>
      <TR><TD ALIGN="LEFT">updated_at : TIMESTAMP WITH TIME ZONE</TD></TR>
    </TABLE>>]


    chats [label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
      <TR><TD BGCOLOR="lightblue"><b>chats</b></TD></TR>
      <TR><TD ALIGN="LEFT">chat_id : UUID (PK)</TD></TR>
      <TR><TD ALIGN="LEFT">user_id : UUID (FK to users)</TD></TR>
      <TR><TD ALIGN="LEFT">chat_title : VARCHAR(255)</TD></TR>
      <TR><TD ALIGN="LEFT">chat_description : TEXT</TD></TR>
      <TR><TD ALIGN="LEFT">session_status : VARCHAR(50)</TD></TR>
      <TR><TD ALIGN="LEFT">created_at : TIMESTAMP WITH TIME ZONE</TD></TR>
      <TR><TD ALIGN="LEFT">updated_at : TIMESTAMP WITH TIME ZONE</TD></TR>
      <TR><TD ALIGN="LEFT">deleted_at : TIMESTAMP WITH TIME ZONE</TD></TR>
      <TR><TD ALIGN="LEFT">chat_mode : VARCHAR(50)</TD></TR>
    </TABLE>>]


    messages [label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
      <TR><TD BGCOLOR="lightblue"><b>messages</b></TD></TR>
      <TR><TD ALIGN="LEFT">message_id : UUID (PK)</TD></TR>
      <TR><TD ALIGN="LEFT">chat_id : UUID (FK to chats)</TD></TR>
      <TR><TD ALIGN="LEFT">user_id : UUID (FK to users) (NULLABLE)</TD></TR>
      <TR><TD ALIGN="LEFT">message_type : VARCHAR(50)</TD></TR>
      <TR><TD ALIGN="LEFT">message_content : TEXT</TD></TR>
      <TR><TD ALIGN="LEFT">created_at : TIMESTAMP WITH TIME ZONE</TD></TR>
      <TR><TD ALIGN="LEFT">deleted_at : TIMESTAMP WITH TIME ZONE</TD></TR>
      <TR><TD ALIGN="LEFT">message_role : VARCHAR(50)</TD></TR>
      <TR><TD ALIGN="LEFT">affects_flowchart : BOOLEAN</TD></TR>
      <TR><TD ALIGN="LEFT">sender_type : VARCHAR(50)</TD></TR>
    </TABLE>>]

    message_attachments [label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
      <TR><TD BGCOLOR="lightblue"><b>message_attachments</b></TD></TR>
      <TR><TD ALIGN="LEFT">attachment_id : UUID (PK)</TD></TR>
      <TR><TD ALIGN="LEFT">message_id : UUID (FK to messages)</TD></TR>
      <TR><TD ALIGN="LEFT">file_name : VARCHAR(255)</TD></TR>
      <TR><TD ALIGN="LEFT">file_type : VARCHAR(255)</TD></TR>
      <TR><TD ALIGN="LEFT">file_size : INTEGER</TD></TR>
      <TR><TD ALIGN="LEFT">file_path : TEXT</TD></TR>
      <TR><TD ALIGN="LEFT">created_at : TIMESTAMP WITH TIME ZONE</TD></TR>
      <TR><TD ALIGN="LEFT">updated_at : TIMESTAMP WITH TIME ZONE</TD></TR>
    </TABLE>>]

    nodes [label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
      <TR><TD BGCOLOR="lightblue"><b>nodes</b></TD></TR>
      <TR><TD ALIGN="LEFT">node_id : UUID (PK)</TD></TR>
      <TR><TD ALIGN="LEFT">flowchart_id : UUID (FK to flowcharts)</TD></TR>
      <TR><TD ALIGN="LEFT">node_type : VARCHAR(50) (ENUM - see description)</TD></TR>
      <TR><TD ALIGN="LEFT">api_name : VARCHAR(255)</TD></TR>
      <TR><TD ALIGN="LEFT">description : TEXT</TD></TR>
      <TR><TD ALIGN="LEFT">parameters : JSONB</TD></TR>
      <TR><TD ALIGN="LEFT">node_data : JSONB</TD></TR>
      <TR><TD ALIGN="LEFT">position_x : INTEGER</TD></TR>
      <TR><TD ALIGN="LEFT">position_y : INTEGER</TD></TR>
      <TR><TD ALIGN="LEFT">created_at : TIMESTAMP WITH TIME ZONE</TD></TR>
      <TR><TD ALIGN="LEFT">updated_at : TIMESTAMP WITH TIME ZONE</TD></TR>
      <TR><TD ALIGN="LEFT">deleted_at : TIMESTAMP WITH TIME ZONE</TD></TR>
    </TABLE>>]

    edges [label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
      <TR><TD BGCOLOR="lightblue"><b>edges</b></TD></TR>
      <TR><TD ALIGN="LEFT">edge_id : UUID (PK)</TD></TR>
      <TR><TD ALIGN="LEFT">flowchart_id : UUID (FK to flowcharts)</TD></TR>
      <TR><TD ALIGN="LEFT">source_node_id : UUID (FK to nodes)</TD></TR>
      <TR><TD ALIGN="LEFT">target_node_id : UUID (FK to nodes)</TD></TR>
      <TR><TD ALIGN="LEFT">edge_type : VARCHAR(50) (ENUM - see description)</TD></TR>
      <TR><TD ALIGN="LEFT">edge_label : VARCHAR(255)</TD></TR>
      <TR><TD ALIGN="LEFT">description : TEXT</TD></TR>
      <TR><TD ALIGN="LEFT">edge_data : JSONB</TD></TR>
      <TR><TD ALIGN="LEFT">created_at : TIMESTAMP WITH TIME ZONE</TD></TR>
      <TR><TD ALIGN="LEFT">updated_at : TIMESTAMP WITH TIME ZONE</TD></TR>
      <TR><TD ALIGN="LEFT">deleted_at : TIMESTAMP WITH TIME ZONE</TD></TR>
    </TABLE>>]
  
  flowchart_chats [label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
      <TR><TD BGCOLOR="lightblue"><b>flowchart_chats</b></TD></TR>
      <TR><TD ALIGN="LEFT">flowchart_chat_id : UUID (PK)</TD></TR>
      <TR><TD ALIGN="LEFT">flowchart_id : UUID (FK to flowcharts)</TD></TR>
      <TR><TD ALIGN="LEFT">chat_id : UUID (FK to chats)</TD></TR>
      <TR><TD ALIGN="LEFT">created_at : TIMESTAMP WITH TIME ZONE</TD></TR>
      <TR><TD ALIGN="LEFT">updated_at : TIMESTAMP WITH TIME ZONE</TD></TR>
    </TABLE>>]

    flowcharts -> users [label="creator_user_id -> user_id", taillabel="1", headlabel="*"]
    flowchart_versions -> flowcharts [label="flowchart_id -> flowchart_id", taillabel="*", headlabel="1"]

    nodes -> flowcharts [label="flowchart_id -> flowchart_id", taillabel="*", headlabel="1"]

    edges -> flowcharts [label="flowchart_id -> flowchart_id", taillabel="*", headlabel="1"]
    edges -> nodes [label="source_node_id -> node_id", taillabel="*", headlabel="1"]
    edges -> nodes [label="target_node_id -> node_id", taillabel="*", headlabel="1"]


    messages -> chats [label="chat_id -> chat_id", taillabel="*", headlabel="1"]
    messages -> users [label="user_id -> user_id", taillabel="*", headlabel="1"]
    message_attachments -> messages [label="message_id -> message_id", taillabel="*", headlabel="1"]

    flowchart_chats -> flowcharts [label="flowchart_id -> flowchart_id", taillabel="*", headlabel="1"]
    flowchart_chats -> chats [label="chat_id -> chat_id", taillabel="*", headlabel="1"]
}