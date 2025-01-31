import ReactFlow, { Controls } from 'reactflow';
import 'reactflow/dist/style.css';

// 超边渲染组件
const HyperEdge = ({ data }) => (
  <div style={{ backgroundColor: '#ff6b6b', padding: 5 }}>
    {data.label} (协作机器人: {data.robots.join(',')})
  </div>
);

const nodes = [
  { id: '1', position: { x: 0, y: 0 }, data: { label: '机械臂A取料', speed: 0.5 } },
  { id: '2', position: { x: 200, y: -100 }, data: { label: '机械臂B定位' } },
  { id: '3', position: { x: 200, y: 100 }, data: { label: '机械臂C辅助' } },
];

const edges = [
  {
    id: 'e1-2-3',
    source: '1',
    targets: ['2', '3'],
    data: { label: '协同搬运', robots: ['A', 'B', 'C'] },
    type: 'hyperEdge',
  },
];

const App = () => (
  <div style={{ height: 400 }}>
    <ReactFlow 
      nodes={nodes} 
      edges={edges}
      edgeTypes={{ hyperEdge: HyperEdge }}
    />
    <Controls />
  </div>
);

export default App;
