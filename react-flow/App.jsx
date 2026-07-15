import { useCallback, useEffect, useMemo, useState } from "react";
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

const PREDEFINED_NODE_TEMPLATES = {
  save_to_file: {
    label: "save_to_file",
    inputCount: 2,
    outputCount: 1,
    params: {
      type: "save_to_file",
      file_path: "",
    },
    paramOrder: [
      "type",
      "file_path",
    ],
    paramTypes: {
      type: "string",
      file_path: "string",
    },
    paramValidators: {
      file_path: "path",
    },
    lockedParams: ["type"],
  },
  container_deployment_kubernetes: {
    label: "container_deployment_kubernetes",
    inputCount: 1,
    outputCount: 1,
    params: {
      type: "container_deployment_kubernetes",
      deployment_name: "",
      replicas: 1,
      namespace: "",
      image_name: "",
      image_tag: "",
      registry: null,
      image_pull_policy: "IfNotPresent",
    },
    paramOrder: [
      "type",
      "deployment_name",
      "replicas",
      "namespace",
      "image_name",
      "image_tag",
      "registry",
      "image_pull_policy",
    ],
    paramTypes: {
      type: "string",
      deployment_name: "string",
      replicas: "int",
      namespace: "string",
      image_name: "string",
      image_tag: "string",
      registry: "string",
      image_pull_policy: "string",
    },
    paramOptions: {
      image_pull_policy: ["Always", "IfNotPresent", "Never"],
    },
    nullableParams: ["registry"],
    lockedParams: ["type"],
  },
  zipper: {
    label: "zipper",
    inputCount: 1,
    outputCount: 1,
    params: {
      type: "zipper",
      target_directory: "",
      output_path: "",
    },
    paramOrder: [
      "type",
      "target_directory",
      "output_path",
    ],
    paramTypes: {
      type: "string",
      target_directory: "string",
      output_path: "string",
    },
    paramValidators: {
      target_directory: "path",
      output_path: "path",
    },
    lockedParams: ["type"],
  },
  data_file: {
    label: "data_file",
    inputCount: 1,
    outputCount: 2,
    params: {
      type: "data_file",
      adapter_type: "",
      provider_bpn: "",
      provider_url: "",
      asset_id: "",
    },
    paramOrder: [
      "type",
      "adapter_type",
      "provider_bpn",
      "provider_url",
      "asset_id",
    ],
    paramTypes: {
      type: "string",
      adapter_type: "string",
      provider_bpn: "string",
      provider_url: "string",
      asset_id: "string",
    },
    paramValidators: {
      provider_url: "url",
    },
    lockedParams: ["type"],
  },
  container_image: {
    label: "container_image",
    inputCount: 1,
    outputCount: 1,
    params: {
      type: "container_image",
      adapter_type: "",
      provider_bpn: "",
      provider_url: "",
      asset_id: "",

      representation: "dockerfile",
      platforms: [],

      image_name: "",
      image_tag: "",
      registry_addr: null,
    },
    paramOrder: [
      "type",
      "adapter_type",
      "provider_bpn",
      "provider_url",
      "asset_id",
      "representation",
      "platforms",
      "image_name",
      "image_tag",
      "registry_addr",
    ],
    paramTypes: {
      type: "string",
      adapter_type: "string",
      provider_bpn: "string",
      provider_url: "string",
      asset_id: "string",

      representation: "string",
      platforms: "array",

      image_name: "string",
      image_tag: "string",
      registry_addr: "string",
    },
    paramOptions: {
      representation: [
        "dockerfile",
        "archive",
      ],
      platforms: [
        "linux/amd64",
        "linux/arm64",
        "windows/amd64",
        "windows/arm64",
      ],
    },
    paramValidators: {
      provider_url: "url",
    },
    nullableParams: ["registry_addr"],
    lockedParams: ["type"],
  },
  unzipper: {
    label: "unzipper",
    inputCount: 1,
    outputCount: 1,
    params: {
      type: "unzipper",
      target_zip: "",
      extract_directory: "",
    },
    paramOrder: [
      "type",
      "target_zip",
      "extract_directory",
    ],
    paramTypes: {
      type: "string",
      target_zip: "string",
      extract_directory: "string",
    },
    paramValidators: {
      target_zip: "path",
      extract_directory: "path",
    },
    lockedParams: ["type"],
  },
  send_to_url: {
    label: "send_to_url",
    inputCount: 2,
    outputCount: 2,
    params: {
      type: "send_to_url",
      url: "",
      method: "POST",
      timeout: 30.0,
    },
    paramOrder: [
      "type",
      "url",
      "method",
      "timeout",
    ],
    paramTypes: {
      type: "string",
      url: "string",
      method: "string",
      timeout: "number",
    },
    paramOptions: {
      method: [
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
      ],
    },
    paramValidators: {
      url: "url",
    },
    lockedParams: ["type"],
  },
};

function CustomNode({ data }) {
  const inputCount = Math.max(1, Number(data.inputCount) || 1);
  const outputCount = Math.max(1, Number(data.outputCount) || 1);
  const paramOrder = data.paramOrder || Object.keys(data.params || {});

  const getInputPortName = (index) =>
    index === 0 ? "dep" : `input_${index - 1}`;
  const getOutputPortName = (index) =>
    index === 0 ? "dep" : `output_${index - 1}`;

  return (
    <div
      style={{
        width: 340,
        padding: "12px 86px",
        border: "1px solid #333",
        borderRadius: 8,
        background: "white",
        boxSizing: "border-box",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {Array.from({ length: inputCount }).map((_, index) => {
        const portName = getInputPortName(index);
        const top = `${((index + 1) / (inputCount + 1)) * 100}%`;

        return (
          <div key={`input-${portName}`}>
            <Handle
              id={portName}
              type="target"
              position={Position.Left}
              style={{ top }}
            />
            <span
              style={{
                position: "absolute",
                left: 10,
                top,
                transform: "translateY(-50%)",
                maxWidth: 72,
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
                fontSize: 10,
                color: "#555",
                pointerEvents: "none",
              }}
              title={portName}
            >
              {portName}
            </span>
          </div>
        );
      })}

      <div
        style={{
          fontWeight: 700,
          overflow: "hidden",
          textOverflow: "ellipsis",
          whiteSpace: "nowrap",
        }}
        title={data.label}
      >
        {data.label}
      </div>

      <div style={{ fontSize: 12, marginTop: 8 }}>
        {paramOrder.map((key) => {
          const parameterValue = data.params?.[key];
          const displayValue =
            parameterValue !== null && typeof parameterValue === "object"
              ? JSON.stringify(parameterValue)
              : String(parameterValue);
          const parameterText = `${key}: ${displayValue}`;

          return (
            <div
              key={key}
              style={{
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
              title={parameterText}
            >
              {parameterText}
            </div>
          );
        })}
      </div>

      <div style={{ fontSize: 11, marginTop: 8, color: "#666" }}>
        inputs: {inputCount}, outputs: {outputCount}
      </div>

      {Array.from({ length: outputCount }).map((_, index) => {
        const portName = getOutputPortName(index);
        const top = `${((index + 1) / (outputCount + 1)) * 100}%`;

        return (
          <div key={`output-${portName}`}>
            <Handle
              id={portName}
              type="source"
              position={Position.Right}
              style={{ top }}
            />
            <span
              style={{
                position: "absolute",
                right: 10,
                top,
                transform: "translateY(-50%)",
                maxWidth: 72,
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
                textAlign: "right",
                fontSize: 10,
                color: "#555",
                pointerEvents: "none",
              }}
              title={portName}
            >
              {portName}
            </span>
          </div>
        );
      })}
    </div>
  );
}

export default function App() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const [selectedEdgeId, setSelectedEdgeId] = useState(null);
  const [newParamName, setNewParamName] = useState("");
  const [newParamType, setNewParamType] = useState("string");
  const [newParamValue, setNewParamValue] = useState("");
  const [editingParamKey, setEditingParamKey] = useState(null);
  const [editingParamType, setEditingParamType] = useState("string");
  const [editingParamValue, setEditingParamValue] = useState("");
  const [selectedTemplateKey, setSelectedTemplateKey] = useState("save_to_file");

  const nodeTypes = useMemo(() => ({ custom: CustomNode }), []);
  const selectedNode = nodes.find((node) => node.id === selectedNodeId);
  const selectedEdge = edges.find((edge) => edge.id === selectedEdgeId);

  const getParamOrder = (node) =>
    node.data.paramOrder || Object.keys(node.data.params || {});

  const inferParamType = (value) => {
    if (typeof value === "boolean") return "bool";
    if (typeof value === "number" && Number.isInteger(value)) return "int";
    if (value !== null && typeof value === "object") return "object";
    return "string";
  };

  const formatParamValue = (value, type = inferParamType(value)) => {
    if (type === "object") return JSON.stringify(value, null, 2);
    return String(value);
  };

  const parseParamValue = (rawValue, type) => {
    if (type === "string") return rawValue;

    if (type === "int") {
      if (!/^-?\d+$/.test(rawValue.trim())) {
        throw new Error("Integer values must contain only whole numbers.");
      }
      return Number.parseInt(rawValue, 10);
    }

    if (type === "bool") {
      if (rawValue === "true") return true;
      if (rawValue === "false") return false;
      throw new Error("Boolean values must be true or false.");
    }

    if (type === "object") {
      const parsed = JSON.parse(rawValue);
      if (parsed === null || Array.isArray(parsed) || typeof parsed !== "object") {
        throw new Error('Object values must use JSON object syntax, for example {"key": 1}.');
      }
      return parsed;
    }

    return rawValue;
  };

  const createNodePosition = (currentNodes) => ({
    x: 100 + currentNodes.length * 30,
    y: 100 + currentNodes.length * 30,
  });

  const addNode = () => {
    const id = `node-${Date.now()}`;

    setNodes((currentNodes) => [
      ...currentNodes,
      {
        id,
        type: "custom",
        position: createNodePosition(currentNodes),
        data: {
          label: `Node ${currentNodes.length + 1}`,
          params: {},
          paramOrder: [],
          paramTypes: {},
          inputCount: 1,
          outputCount: 1,
        },
      },
    ]);
  };

  const addPredefinedNode = () => {
    const template = PREDEFINED_NODE_TEMPLATES[selectedTemplateKey];
    if (!template) return;

    const id = `${selectedTemplateKey}-${Date.now()}`;

    setNodes((currentNodes) => [
      ...currentNodes,
      {
        id,
        type: "custom",
        position: createNodePosition(currentNodes),
        data: {
          label: template.label,
          templateKey: selectedTemplateKey,
          isPredefined: true,
          params: { ...template.params },
          paramOrder: [...template.paramOrder],
          paramTypes: { ...template.paramTypes },
          paramValidators: { ...template.paramValidators },
          lockedParams: [...(template.lockedParams || [])],
          inputCount: template.inputCount,
          outputCount: template.outputCount,
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
    const nextValue = Math.max(1, Number(value) || 1);

    setNodes((currentNodes) =>
      currentNodes.map((node) =>
        node.id === selectedNodeId
          ? { ...node, data: { ...node.data, [key]: nextValue } }
          : node
      )
    );
  };

  const addParameter = () => {
    const key = newParamName.trim();
    if (!selectedNodeId || !key) {
      alert("Enter a parameter name.");
      return;
    }

    try {
      const parsedValue = parseParamValue(newParamValue, newParamType);

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
                [key]: parsedValue,
              },
              paramTypes: {
                ...node.data.paramTypes,
                [key]: newParamType,
              },
              paramOrder: alreadyExists ? currentOrder : [...currentOrder, key],
            },
          };
        })
      );

      setNewParamName("");
      setNewParamType("string");
      setNewParamValue("");
    } catch (error) {
      alert(error.message);
    }
  };

  const startEditingParameter = (key) => {
    if ((selectedNode.data.lockedParams || []).includes(key)) return;

    const value = selectedNode.data.params?.[key];
    const type = selectedNode.data.paramTypes?.[key] || inferParamType(value);

    setEditingParamKey(key);
    setEditingParamType(type);
    setEditingParamValue(formatParamValue(value, type));
  };

  const saveEditedParameter = () => {
    if ((selectedNode?.data.lockedParams || []).includes(editingParamKey)) {
      alert("This parameter is fixed by the predefined template.");
      return;
    }

    try {
      const parsedValue = parseParamValue(editingParamValue, editingParamType);
      const validator = selectedNode?.data.paramValidators?.[editingParamKey];

      if (validator === "url") {
        try {
          new URL(String(parsedValue));
        } catch {
          throw new Error("provider_url must be a valid URL, including http:// or https://.");
        }
      }

      setNodes((currentNodes) =>
        currentNodes.map((node) =>
          node.id === selectedNodeId
            ? {
                ...node,
                data: {
                  ...node.data,
                  params: {
                    ...node.data.params,
                    [editingParamKey]: parsedValue,
                  },
                  paramTypes: {
                    ...node.data.paramTypes,
                    [editingParamKey]: editingParamType,
                  },
                },
              }
            : node
        )
      );

      setEditingParamKey(null);
    } catch (error) {
      alert(error.message);
    }
  };

  const removeParameter = (keyToRemove) => {
    setNodes((currentNodes) =>
      currentNodes.map((node) => {
        if (node.id !== selectedNodeId) return node;

        const nextParams = { ...node.data.params };
        const nextParamTypes = { ...node.data.paramTypes };
        delete nextParams[keyToRemove];
        delete nextParamTypes[keyToRemove];

        return {
          ...node,
          data: {
            ...node.data,
            params: nextParams,
            paramTypes: nextParamTypes,
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

  const deleteSelectedNode = useCallback(() => {
    if (!selectedNodeId) return;

    setNodes((currentNodes) =>
      currentNodes.filter((node) => node.id !== selectedNodeId)
    );

    setEdges((currentEdges) =>
      currentEdges.filter(
        (edge) =>
          edge.source !== selectedNodeId &&
          edge.target !== selectedNodeId &&
          edge.id !== selectedEdgeId
      )
    );

    setSelectedNodeId(null);
    setSelectedEdgeId(null);
  }, [selectedNodeId, selectedEdgeId]);

  const deleteSelectedEdge = useCallback(() => {
    if (!selectedEdgeId) return;

    setEdges((currentEdges) =>
      currentEdges.filter((edge) => edge.id !== selectedEdgeId)
    );

    setSelectedEdgeId(null);
  }, [selectedEdgeId]);

  const deleteSelected = useCallback(() => {
    if (selectedNodeId) {
      deleteSelectedNode();
      return;
    }

    if (selectedEdgeId) {
      deleteSelectedEdge();
    }
  }, [selectedNodeId, selectedEdgeId, deleteSelectedNode, deleteSelectedEdge]);

  useEffect(() => {
    setEditingParamKey(null);
    setNewParamName("");
    setNewParamType("string");
    setNewParamValue("");
  }, [selectedNodeId]);

  useEffect(() => {
    const handleKeyDown = (event) => {
      const tagName = event.target.tagName;
      const isTyping = ["INPUT", "TEXTAREA", "SELECT"].includes(tagName);

      if (isTyping) return;

      if (event.key === "Delete" || event.key === "Backspace") {
        deleteSelected();
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [deleteSelected]);

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

  const importJson = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();

    reader.onload = (readerEvent) => {
      try {
        const graph = JSON.parse(readerEvent.target.result);

        if (!Array.isArray(graph.nodes) || !Array.isArray(graph.edges)) {
          alert("Invalid graph JSON. Expected { nodes: [], edges: [] }.");
          return;
        }

        const normalizedNodes = graph.nodes.map((node) => {
          const template = node.data?.templateKey
            ? PREDEFINED_NODE_TEMPLATES[node.data.templateKey]
            : null;
          const params = template
            ? { ...template.params, ...(node.data?.params || {}) }
            : { ...(node.data?.params || {}) };

          if (template?.lockedParams?.includes("type")) {
            params.type = template.params.type;
          }

          return {
            ...node,
            data: {
              ...node.data,
              params,
              paramOrder: template
                ? [...template.paramOrder]
                : node.data?.paramOrder || Object.keys(params),
              inputCount: template
                ? template.inputCount
                : Math.max(1, Number(node.data?.inputCount) || 1),
              outputCount: template
                ? template.outputCount
                : Math.max(1, Number(node.data?.outputCount) || 1),
              paramTypes: template
                ? { ...template.paramTypes }
                : Object.fromEntries(
                    Object.entries(params).map(([key, value]) => [
                      key,
                      node.data?.paramTypes?.[key] || inferParamType(value),
                    ])
                  ),
              paramValidators: template
                ? { ...template.paramValidators }
                : { ...(node.data?.paramValidators || {}) },
              lockedParams: template
                ? [...(template.lockedParams || [])]
                : [...(node.data?.lockedParams || [])],
            },
          };
        });

        setNodes(normalizedNodes);
        setEdges(graph.edges);
        setSelectedNodeId(null);
        setSelectedEdgeId(null);

        alert("Import completed.");
      } catch (error) {
        console.error(error);
        alert("Invalid JSON file.");
      }
    };

    reader.readAsText(file);

    event.target.value = "";
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

  const visibleEdges = useMemo(
    () =>
      edges.map((edge) => ({
        ...edge,
        selected: edge.id === selectedEdgeId,
      })),
    [edges, selectedEdgeId]
  );

  return (
    <div
      style={{
        display: "flex",
        position: "fixed",
        inset: 0,
        width: "100vw",
        height: "100vh",
        margin: 0,
        padding: 0,
        textAlign: "left",
      }}
    >
      <aside
        style={{
          width: 340,
          flex: "0 0 340px",
          alignSelf: "stretch",
          padding: 16,
          borderRight: "1px solid #ddd",
          background: "#f7f7f7",
          boxSizing: "border-box",
          overflowY: "auto",
          textAlign: "left",
        }}
      >
        <h2>Graph Editor</h2>

        <button onClick={addNode} style={{ width: "100%", marginBottom: 8 }}>
          + Add Node
        </button>

        <div
          style={{
            display: "flex",
            gap: 6,
            marginBottom: 8,
          }}
        >
          <select
            value={selectedTemplateKey}
            onChange={(event) => setSelectedTemplateKey(event.target.value)}
            style={{ flex: 1, minWidth: 0 }}
          >
            {Object.keys(PREDEFINED_NODE_TEMPLATES).map((templateKey) => (
              <option key={templateKey} value={templateKey}>
                {templateKey}
              </option>
            ))}
          </select>
          <button onClick={addPredefinedNode} style={{ flex: 1.3 }}>
            + Add Predefined Node
          </button>
        </div>

        <button onClick={exportJson} style={{ width: "100%" }}>
          Export JSON
        </button>

        <button
          onClick={() => document.getElementById("import-json").click()}
          style={{ width: "100%", marginTop: 8 }}
        >
          Import JSON
        </button>

        <input
          id="import-json"
          type="file"
          accept=".json,application/json"
          style={{ display: "none" }}
          onChange={importJson}
        />

        <hr />

        {selectedEdge ? (
          <>
            <h3>Selected Edge</h3>

            <p style={{ fontSize: 12 }}>
              {selectedEdge.source} → {selectedEdge.target}
            </p>

            <button
              onClick={deleteSelectedEdge}
              style={{ width: "100%", marginTop: 8 }}
            >
              Delete Edge
            </button>
          </>
        ) : selectedNode ? (
          <>
            <h3>Selected Node</h3>

            <button
              onClick={deleteSelectedNode}
              style={{ width: "100%", marginBottom: 12 }}
            >
              Delete Node
            </button>

            <label>
              Label
              <input
                value={selectedNode.data.label}
                onChange={(event) => updateNodeLabel(event.target.value)}
                style={{
                  width: "100%",
                  marginTop: 4,
                  background: "white",
                }}
              />
            </label>

            {!selectedNode.data.isPredefined && (
              <>
                <h4>Add Parameter</h4>

                <input
              value={newParamName}
              onChange={(event) => setNewParamName(event.target.value)}
              placeholder="Parameter name"
              style={{ width: "100%", boxSizing: "border-box", marginBottom: 6 }}
            />

            <select
              value={newParamType}
              onChange={(event) => {
                const nextType = event.target.value;
                setNewParamType(nextType);
                setNewParamValue(nextType === "bool" ? "true" : nextType === "object" ? "{}" : "");
              }}
              style={{ width: "100%", marginBottom: 6 }}
            >
              <option value="string">string</option>
              <option value="int">int</option>
              <option value="bool">bool</option>
              <option value="object">object {}</option>
            </select>

            {newParamType === "bool" ? (
              <select
                value={newParamValue || "true"}
                onChange={(event) => setNewParamValue(event.target.value)}
                style={{ width: "100%", marginBottom: 6 }}
              >
                <option value="true">true</option>
                <option value="false">false</option>
              </select>
            ) : newParamType === "object" ? (
              <textarea
                value={newParamValue}
                onChange={(event) => setNewParamValue(event.target.value)}
                placeholder='{"key": 1}'
                rows={4}
                style={{ width: "100%", boxSizing: "border-box", marginBottom: 6 }}
              />
            ) : (
              <input
                type={newParamType === "int" ? "number" : "text"}
                step={newParamType === "int" ? "1" : undefined}
                value={newParamValue}
                onChange={(event) => setNewParamValue(event.target.value)}
                placeholder="Parameter value"
                style={{ width: "100%", boxSizing: "border-box", marginBottom: 6 }}
              />
            )}

                <button onClick={addParameter} style={{ width: "100%" }}>
                  + Add Parameter
                </button>
              </>
            )}

            {selectedNode.data.isPredefined && (
              <p style={{ fontSize: 12, color: "#666" }}>
                Template: <strong>{selectedNode.data.templateKey}</strong>.
                The label and parameter values can be edited. Parameter names, types, ports, and locked fields are fixed.
              </p>
            )}

            <h4>Parameters</h4>

            {selectedParamOrder.length === 0 ? (
              <p>No parameters.</p>
            ) : (
              selectedParamOrder.map((key, index) => {
                const value = selectedNode.data.params?.[key];
                const type =
                  selectedNode.data.paramTypes?.[key] || inferParamType(value);
                const displayValue =
                  type === "object" ? JSON.stringify(value) : String(value);
                const isEditing = editingParamKey === key;
                const isLockedParam = (selectedNode.data.lockedParams || []).includes(key);

                return (
                  <div
                    key={key}
                    style={{
                      background: "white",
                      padding: 8,
                      marginBottom: 6,
                      border: "1px solid #ddd",
                      borderRadius: 4,
                    }}
                  >
                    {isEditing ? (
                      <>
                        <div style={{ fontSize: 12, marginBottom: 6 }}>
                          <strong>{key}</strong>
                        </div>

                        <select
                          value={editingParamType}
                          disabled={Boolean(selectedNode.data.isPredefined)}
                          onChange={(event) => {
                            const nextType = event.target.value;
                            setEditingParamType(nextType);
                            setEditingParamValue(
                              nextType === "bool"
                                ? "true"
                                : nextType === "object"
                                  ? "{}"
                                  : ""
                            );
                          }}
                          style={{
                            width: "100%",
                            marginBottom: 6,
                            background: selectedNode.data.isPredefined ? "#eee" : "white",
                          }}
                        >
                          <option value="string">string</option>
                          <option value="int">int</option>
                          <option value="bool">bool</option>
                          <option value="object">object {}</option>
                        </select>

                        {editingParamType === "bool" ? (
                          <select
                            value={editingParamValue}
                            onChange={(event) =>
                              setEditingParamValue(event.target.value)
                            }
                            style={{ width: "100%", marginBottom: 6 }}
                          >
                            <option value="true">true</option>
                            <option value="false">false</option>
                          </select>
                        ) : editingParamType === "object" ? (
                          <textarea
                            value={editingParamValue}
                            onChange={(event) =>
                              setEditingParamValue(event.target.value)
                            }
                            rows={4}
                            style={{
                              width: "100%",
                              boxSizing: "border-box",
                              marginBottom: 6,
                            }}
                          />
                        ) : (
                          <input
                            type={editingParamType === "int" ? "number" : "text"}
                            step={editingParamType === "int" ? "1" : undefined}
                            value={editingParamValue}
                            onChange={(event) =>
                              setEditingParamValue(event.target.value)
                            }
                            style={{
                              width: "100%",
                              boxSizing: "border-box",
                              marginBottom: 6,
                            }}
                          />
                        )}

                        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                          <button onClick={saveEditedParameter} style={{ flex: 1 }}>
                            Save
                          </button>
                          <button
                            onClick={() => setEditingParamKey(null)}
                            style={{ flex: 1 }}
                          >
                            Cancel
                          </button>
                        </div>
                      </>
                    ) : (
                      <>
                        <div
                          style={{
                            fontSize: 12,
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                            whiteSpace: "nowrap",
                            marginBottom: 6,
                          }}
                          title={`${key}: ${displayValue}`}
                        >
                          <strong>{key}</strong> ({type}): {displayValue}
                        </div>

                        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                          {!selectedNode.data.isPredefined && (
                            <>
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
                            </>
                          )}
                          <button
                            onClick={() => startEditingParameter(key)}
                            disabled={isLockedParam}
                            title={isLockedParam ? "This parameter is fixed by the template." : undefined}
                            style={{ fontWeight: 600 }}
                          >
                            {isLockedParam ? "Fixed" : "Edit value"}
                          </button>
                          {!selectedNode.data.isPredefined && (
                            <button onClick={() => removeParameter(key)}>
                              Remove
                            </button>
                          )}
                        </div>
                      </>
                    )}
                  </div>
                );
              })
            )}

            <h4>Ports</h4>

            <label>
              Input count
              <input
                type="number"
                min="1"
                disabled={Boolean(selectedNode.data.isPredefined)}
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
                min="1"
                disabled={Boolean(selectedNode.data.isPredefined)}
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

      <main style={{ flex: 1, minWidth: 0 }}>
        <ReactFlow
          nodes={nodes}
          edges={visibleEdges}
          nodeTypes={nodeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={(_, node) => {
            setSelectedNodeId(node.id);
            setSelectedEdgeId(null);
          }}
          onEdgeClick={(_, edge) => {
            setSelectedEdgeId(edge.id);
            setSelectedNodeId(null);
          }}
          onPaneClick={() => {
            setSelectedNodeId(null);
            setSelectedEdgeId(null);
          }}
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