// src/App.jsx
import React, { useState } from 'react';
import { Neo4jGraph } from '@neo4j-labs/graph-explorer';

const App = () => {
  const [command, setCommand] = useState('');
  const [graphData, setGraphData] = useState(null);
  const [generatedCode, setGeneratedCode] = useState('');

  const handleSubmit = async () => {
    const response = await fetch('http://localhost:8000/process_command', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        text: command,
        session_id: 'user_123' 
      })
    });
    
    const result = await response.json();
    setGraphData(result.graph);
    setGeneratedCode(result.code);
    
    if (result.errors.length > 0) {
      alert(`发现错误：\n${result.errors.join('\n')}`);
    }
  };

  return (
    <div style={{display: 'flex', height: '100vh'}}>
      <div style={{width: '30%', padding: 20}}>
        <textarea 
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          placeholder="输入自然语言指令，例如：让机器人A和B协同搬运物料"
          style={{width: '100%', height: 100}}
        />
        <button onClick={handleSubmit}>生成流程图</button>
        
        <h3>生成代码：</h3>
        <pre style={{background: '#eee', padding: 10}}>
          {generatedCode}
        </pre>
      </div>
      
      <div style={{width: '70%'}}>
        {graphData && (
          <Neo4jGraph
            nodes={graphData.nodes}
            relationships={graphData.edges}
            onNodeClick={node => console.log('选中节点:', node)}
            onRelationshipCreate={(start, end) => 
              console.log('创建连接:', start, end)
            }
          />
        )}
      </div>
    </div>
  );
};

export default App;