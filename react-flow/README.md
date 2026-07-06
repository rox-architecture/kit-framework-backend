# Test Purpose Graph Editor GUI

We want to test our workflow execution engine with various workflow graphs and nodes.
For this, an easy-to-use graph editor will be useful. 
With this, we can quickly create and modify the workflow graphs to observe the results of the engine.

## Install

From the repository root, go to the react-flow directory:
```
cd react-flow
```

Then, install a React-Flow server. You need `npm`.
```
npm create vite@latest react-flow-editor -- --template react
cd react-flow-editor
npm install
npm install @xyflow/react
```

In the `react-flow-editor` directory, overwrite the `react-App.jsx` file with the provided one
```
cp ../App.jsx src/App.jsx
```

Check if everything is installed correctly
```
npm list @xyflow/react
```

If (empty) is shown, then try again:
```
npm install @xyflow/react
```

Now, run the GUI by:
```
npm run dev
```

## Notes:

- Use this GUI to quickly create a testing workflow graph
- Export the graph to JSON
- Our workflow execution engine takes the graph JSON to execute

