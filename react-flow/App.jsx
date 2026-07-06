import { useCallback, useMemo, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Handle,
  Position,
  addEdge,
  applyNodeChanges,
  applyEdgeChanges,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

function CustomNode({ data }) {
  const inputCount = data.inputCount ?? 1;
  const outputCount = data.outputCount ?? 1;
  const paramOrder = data.paramOrder || Object.keys(data.params || {});

  return (
    <div
      style={{
        padding: 12,
        border: "1px solid #333",
        borderRadius: 8,
        background: "white",
        minWidth: 150,
        position: "relative",
      }}
    >
      {Array.from({ length: inputCount }).map((_, index) => (
        <Handle
          key={`input_${index}`}
          id={`input_${index}`}
          type="target"
          position={Position.Left}
          style={{ top: `${((index + 1) / (inputCount + 1)) * 100}%` }}
        />
      ))}

      <b>{data.label}</b>

      <div style={{ fontSize: 12, marginTop: 8 }}>
        {paramOrder.map((key) => (
          <div key={key}>
            {key}: {String(data.params?.[key])}
          </div>
        ))}
      </div>

      <div style={{ fontSize: 11, marginTop: 8, color: "#666" }}>
        inputs: {inputCount}, outputs: {outputCount}
      </div>

      {Array.from({ length: outputCount }).map((_, index) => (
        <Handle
          key={`output_${index}`}
          id={`output_${index}`}
          type="source"
          position={Position.Right}
          style={{ top: `${((index + 1) / (outputCount + 1)) * 100}%` }}
        />
      ))}
    </div>
  );
}

export default function App() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [selectedNodeId, setSelectedNodeId] = useState(null);

  const nodeTypes = useMemo(() => ({ custom: CustomNode }), []);
  const selectedNode = nodes.find((node) => node.id === selectedNodeId);

  const getParamOrder = (node) =>
    node.data.paramOrder || Object.keys(node.data.params || {});

  const addNode = () => {
    const id = `node-${Date.now()}`;

    setNodes((currentNodes) => [
      ...currentNodes,
      {
        id,
        type: "custom",
        position: {
          x: 100 + currentNodes.length * 30,
          y: 100 + currentNodes.length * 30,
        },
        data: {
          label: `Node ${currentNodes.length + 1}`,
          params: {},
          paramOrder: [],
          inputCount: 1,
          outputCount: 1,
        },
      },
    ]);
  };

  const updateNodeLabel = (label) => {
    setNodes((currentNodes) =>
      currentNodes.map((node) =>
        node.id === selectedNodeId
          ? { ...node, data: { ...node.data, label } }
          : node
      )
    );
  };

  const updatePortCount = (key, value) => {
    const nextValue = Math.max(0, Number(value));

    setNodes((currentNodes) =>
      currentNodes.map((node) =>
        node.id === selectedNodeId
          ? { ...node, data: { ...node.data, [key]: nextValue } }
          : node
      )
    );
  };

  const addParameter = () => {
    if (!selectedNodeId) {
      alert("Select a node first.");
      return;
    }

    const key = prompt("Parameter name");
    if (!key) return;

    const value = prompt("Parameter value");
    if (value === null) return;

    setNodes((currentNodes) =>
      currentNodes.map((node) => {
        if (node.id !== selectedNodeId) return node;

        const currentOrder = getParamOrder(node);
        const alreadyExists = Object.prototype.hasOwnProperty.call(
          node.data.params || {},
          key
        );

        return {
          ...node,
          data: {
            ...node.data,
            params: {
              ...node.data.params,
              [key]: value,
            },
            paramOrder: alreadyExists ? currentOrder : [...currentOrder, key],
          },
        };
      })
    );
  };

  const removeParameter = (keyToRemove) => {
    setNodes((currentNodes) =>
      currentNodes.map((node) => {
        if (node.id !== selectedNodeId) return node;

        const nextParams = { ...node.data.params };
        delete nextParams[keyToRemove];

        return {
          ...node,
          data: {
            ...node.data,
            params: nextParams,
            paramOrder: getParamOrder(node).filter((key) => key !== keyToRemove),
          },
        };
      })
    );
  };

  const moveParameter = (key, direction) => {
    setNodes((currentNodes) =>
      currentNodes.map((node) => {
        if (node.id !== selectedNodeId) return node;

        const order = getParamOrder(node);
        const index = order.indexOf(key);
        const newIndex = direction === "up" ? index - 1 : index + 1;

        if (index === -1 || newIndex < 0 || newIndex >= order.length) {
          return node;
        }

        const nextOrder = [...order];
        [nextOrder[index], nextOrder[newIndex]] = [
          nextOrder[newIndex],
          nextOrder[index],
        ];

        return {
          ...node,
          data: {
            ...node.data,
            paramOrder: nextOrder,
          },
        };
      })
    );
  };

  const exportJson = () => {
    const graph = { nodes, edges };
    const json = JSON.stringify(graph, null, 2);
    console.log(json);

    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");

    anchor.href = url;
    anchor.download = "graph.json";
    anchor.click();

    URL.revokeObjectURL(url);
  };

  const onNodesChange = useCallback((changes) => {
    setNodes((currentNodes) => applyNodeChanges(changes, currentNodes));
  }, []);

  const onEdgesChange = useCallback((changes) => {
    setEdges((currentEdges) => applyEdgeChanges(changes, currentEdges));
  }, []);

  const onConnect = useCallback((connection) => {
    setEdges((currentEdges) =>
      addEdge({ ...connection, animated: true }, currentEdges)
    );
  }, []);

  const selectedParamOrder = selectedNode
    ? selectedNode.data.paramOrder || Object.keys(selectedNode.data.params || {})
    : [];

  return (
    <div style={{ display: "flex", width: "100vw", height: "100vh" }}>
      <aside
        style={{
          width: 280,
          padding: 16,
          borderRight: "1px solid #ddd",
          background: "#f7f7f7",
          boxSizing: "border-box",
        }}
      >
        <h2>Graph Editor</h2>

        <button onClick={addNode} style={{ width: "100%", marginBottom: 8 }}>
          + Add Node
        </button>

        <button onClick={exportJson} style={{ width: "100%" }}>
          Export JSON
        </button>

        <hr />

        {selectedNode ? (
          <>
            <h3>Selected Node</h3>

            <label>
              Label
              <input
                value={selectedNode.data.label}
                onChange={(event) => updateNodeLabel(event.target.value)}
                style={{ width: "100%", marginTop: 4 }}
              />
            </label>

            <button
              onClick={addParameter}
              style={{ width: "100%", marginTop: 12 }}
            >
              + Add Parameter
            </button>

            <h4>Parameters</h4>

            {selectedParamOrder.length === 0 ? (
              <p>No parameters.</p>
            ) : (
              selectedParamOrder.map((key, index) => {
                const value = selectedNode.data.params?.[key];

                return (
                  <div
                    key={key}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      gap: 6,
                      background: "white",
                      padding: 8,
                      marginBottom: 6,
                      border: "1px solid #ddd",
                      borderRadius: 4,
                    }}
                  >
                    <div style={{ fontSize: 12, flex: 1 }}>
                      <strong>{key}</strong>: {String(value)}
                    </div>

                    <button
                      onClick={() => moveParameter(key, "up")}
                      disabled={index === 0}
                    >
                      ↑
                    </button>

                    <button
                      onClick={() => moveParameter(key, "down")}
                      disabled={index === selectedParamOrder.length - 1}
                    >
                      ↓
                    </button>

                    <button onClick={() => removeParameter(key)}>Remove</button>
                  </div>
                );
              })
            )}

            <h4>Ports</h4>

            <label>
              Input count
              <input
                type="number"
                min="0"
                value={selectedNode.data.inputCount ?? 1}
                onChange={(event) =>
                  updatePortCount("inputCount", event.target.value)
                }
                style={{ width: "100%", marginTop: 4, marginBottom: 8 }}
              />
            </label>

            <label>
              Output count
              <input
                type="number"
                min="0"
                value={selectedNode.data.outputCount ?? 1}
                onChange={(event) =>
                  updatePortCount("outputCount", event.target.value)
                }
                style={{ width: "100%", marginTop: 4 }}
              />
            </label>
          </>
        ) : (
          <p>Select a node to edit parameters.</p>
        )}
      </aside>

      <main style={{ flex: 1 }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={(_, node) => setSelectedNodeId(node.id)}
          onPaneClick={() => setSelectedNodeId(null)}
          fitView
        >
          <Background />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </main>
    </div>
  );
}