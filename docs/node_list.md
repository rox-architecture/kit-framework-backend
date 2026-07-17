# List of Available Node Types

Each node type defines a specific behaviour with predefined I/O ports and parameters.

All available node types are registered in the node registry:

[`node_registry.py`](./../src/cee/node_plugins/node_registry.py)

The node types are divided into two categories depending on whether they interact with a dataspace:

* **Dataspace**: node types that interact with dataspace assets or adapters.
* **Utility**: node types that perform local or external operations without dataspace interaction.

---

## Type: `ds_data_file`

**Category:** Dataspace

### Description

This node type retrieves a binary file asset from a dataspace.

When executed, it uses the configured adapter to pull the requested asset. If the initial transfer fails, the current implementation automatically initiates a negotiation with the provider and retries the transfer.

The downloaded binary content is packaged into a single `Item` together with metadata such as its content type, content length, provider URL, provider BPN, and asset ID. The resulting item is exposed through the node's first output port.

### Implementation

Input, output, and parameter specifications can be seen in the [source code](./../src/cee/node_plugins/nodes/data_file.py).

---

## Type: `save_to_file`

**Category:** Utility

### Description

This node type writes the binary content of an input `Item` to a local file.

When executed, it validates the input, obtains the binary data from the first input port, and writes it to the configured file path. Any missing parent directories are created automatically.

The node does not produce an output item.

### Implementation

Input, output, and parameter specifications can be seen in the [source code](./../src/cee/node_plugins/nodes/save_to_file.py).

---

## Type: `send_to_url`

**Category:** Utility

### Description

This node type sends an HTTP request to a configured URL.

The HTTP method and timeout can be configured. For methods that contain a request body, the node sends the binary content of the first input `Item` and uses its content type as the HTTP `Content-Type` header.

The HTTP response is packaged into an output `Item` containing the response body, content type, content length, and HTTP status code. Requests returning a `4xx` or `5xx` status raise an exception.

### Implementation

Input, output, and parameter specifications can be seen in the [source code](./../src/cee/node_plugins/nodes/send_to_url.py).

> **Implementation note:** The current `InputSpec` is empty, although the runtime accesses `input_0` for methods other than `GET` and `DELETE`.

---

## Type: `ds_service_file`

**Category:** Dataspace

### Description

This node type invokes a service-backed dataspace asset and returns the response as a file-like `Item`.

When executed, it uses the configured adapter to access an asset with a specified HTTP method, optional subpath, and optional payload. If the initial request fails, the current implementation automatically initiates a negotiation and retries the asset transfer.

The response body is returned as binary data together with metadata describing its content type, content length, provider URL, provider BPN, and asset ID.

### Implementation

Input, output, and parameter specifications can be seen in the [source code](./../src/cee/node_plugins/nodes/service_file.py).

---

## Type: `unzipper`

**Category:** Utility

### Description

This node type extracts a local ZIP archive into a configured directory.

When executed, it verifies that the source archive exists and has a `.zip` extension. It then creates the extraction directory if necessary and extracts the complete archive into it.

The node does not produce an output item.

### Implementation

Input, output, and parameter specifications can be seen in the [source code](./../src/cee/node_plugins/nodes/unzipper.py).

---

## Type: `zipper`

**Category:** Utility

### Description

This node type creates a ZIP archive from a local directory.

When executed, it verifies that the configured source path is a directory, creates any missing output directories, and compresses the directory contents into a ZIP archive. If the configured output path does not end in `.zip`, the extension is added automatically.

The node does not produce an output item.

### Implementation

Input, output, and parameter specifications can be seen in the [source code](./../src/cee/node_plugins/nodes/zipper.py).

---

## Type: `container_deployment_kubernetes`

**Category:** Utility

### Description

This node type deploys a container image to a Kubernetes cluster.

When executed, it loads the local Kubernetes configuration and constructs a Kubernetes `Deployment` using the configured image, deployment name, replica count, namespace, and image pull policy.

The deployment is submitted through the Kubernetes API. If a deployment with the same name already exists, the node raises an error instead of updating or replacing it.

### Implementation

Input, output, and parameter specifications can be seen in the [source code](./../src/cee/node_plugins/nodes/container_dep_kub.py).

---

## Type: `ds_container`

**Category:** Dataspace

### Description

This node type retrieves a container image definition from a dataspace asset.

The asset may contain either a standalone Dockerfile or a ZIP/TAR archive containing a Docker build context. If the initial transfer fails, the current implementation automatically initiates a negotiation and retries the transfer.

The node builds the container image locally using Docker. If a registry address is configured, the resulting image is tagged with the registry address and pushed to that registry.

### Implementation

Input, output, and parameter specifications can be seen in the [source code](./../src/cee/node_plugins/nodes/container_image.py).
