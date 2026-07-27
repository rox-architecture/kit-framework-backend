# Asset Types and Metadata

In a dataspace, a wide variety of resources can be represented as assets, including raw data, configuration files, container images, service endpoints, and continuous data streams.

However, representing all these heterogeneous resources uniformly as assets creates ambiguity regarding how they should be accessed, consumed, deployed, or executed within a system.

To address this ambiguity, the KIT concept (in the RoX project) classifies assets into a few operational types.

## Basic Asset Types

1. **Static File**: A finite data artifact that can be directly transferred (e.g., CSV, JSON, images)
2. **Container**: An executable software package distributed as a container image (e.g., Docker/Archive/OCI image)
3. **File Service**: A service endpoint that returns a finite file upon invocation (e.g., image conversion, report generation)
4. **Streaming Service**: A service endpoint that provides a continuous stream of data (e.g., camera feed)
5. **Workflow**: A JSON-encoded workflow graph that defines the composition, dependencies, and execution order of assets in a KIT-based pipeline.

The last type is a special type that represents an executable workflow rather than an individual data or software asset.

When publishing an asset to the dataspace, **you must assign it with exactly one type**.
You then provide the operational metadata to the asset according to the asset type.
The metadata schema is specified below.

## Static File

| Field                   | Type          | Required | Description                                                                 |
| ----------------------- | ------------- | :------: | --------------------------------------------------------------------------- |
| `operational_type`      | `enum`        |     ✓    | Fixed value: `static_file`.                                                 |
| `semantic_model`        | `JSON object` |     ✓    | JSON object describing the semantic meaning and structure of the asset.     |
| `contact_email`         | `string`      |     ✓    | Email address of the contact person responsible for maintaining the asset.  |
| `file_format`           | `string`      |     ✓    | File format (e.g., `csv`, `json`, `jpg`, `mp4`).                            |
| `file_size`             | `integer`     |          | Size of the file in bytes.                                                  |
| `checksum`              | `string`      |          | SHA-256 checksum used to verify file integrity.                             |
| `encoding`              | `string`      |          | Character encoding for text-based files (e.g., `UTF-8`).                    |
| `hardware_requirements` | `JSON object` |          | Minimum or recommended hardware resources required for execution.           |
| `software_requirements` | `JSON object` |          | Required software, runtime, drivers, or platform dependencies.              |


## Container

| Field                   | Type          | Required | Description                                                                                      |
| ----------------------- | ------------- | :------: | ------------------------------------------------------------------------------------------------ |
| `operational_type`      | `enum`        |     ✓    | Fixed value: `container`.                                                                        |
| `semantic_model`        | `JSON object` |     ✓    | JSON object describing the semantic meaning and capabilities of the asset.                       |
| `contact_email`         | `string`      |     ✓    | Email address of the contact person responsible for maintaining the asset.                       |
| `distribution_type`     | `enum`        |     ✓    | Distribution method of the container asset: `oci_registry`, `image_archive`, or `dockerfile`.    |
| `image_name`            | `string`      |     ✓    | Name of the container image (e.g., `object-detector`).                                           |
| `image_tag`             | `string`      |     ✓    | Tag identifying a specific image version (e.g., `1.2.0`, `latest`).                              |
| `platforms`             | `set<enum>`   |     ✓    | Supported target platforms: `linux/amd64`, `linux/arm64`, `windows/amd64`, `windows/arm64`.      |
| `hardware_requirements` | `JSON object` |          | Minimum or recommended hardware resources required for execution.                                |
| `software_requirements` | `JSON object` |          | Required software, runtime, drivers, or platform dependencies.                                   |


## File Service

| Field                   | Type          | Required | Description                                                                                      |
| ----------------------- | ------------- | :------: | ------------------------------------------------------------------------------------------------ |
| `operational_type`      | `enum`        |    ✓     | Fixed value: `file_service`.                                                                     |
| `semantic_model`        | `JSON object` |    ✓     | RODEOS semantic model describing the semantic meaning and capabilities of the service.           |
| `contact_email`         | `string`      |    ✓     | Email address of the contact person responsible for maintaining the asset.                       |
| `file_format`           | `string`      |    ✓     | Format of the file returned by the service (e.g., `csv`, `json`, `jpg`, `mp4`).                  |
| `request_method`        | `enum`        |    ✓     | HTTP method used to invoke the service (e.g., `GET`, `POST`).                                    |
| `subpath`               | `string`      |    ✓     | Relative API path appended to the service endpoint (e.g., `/convert`, `/reports/generate`).      |
| `api_documentation_url` | `URI`         |          | URL of the API documentation, such as a Swagger UI page or OpenAPI document.                     |


## Streaming Service

Schema definition is WIP


## Workflow

| Field                   | Type            | Required | Description                                                                                   |
| ----------------------- | --------------- | :------: | --------------------------------------------------------------------------------------------- |
| `operational_type`      | `enum`          |     ✓    | Fixed value: `workflow`.                                                                      |
| `contact_email`         | `string`        |     ✓    | Email address of the contact person responsible for maintaining the asset.                    |
| `hardware_requirements` | `JSON object`   |     ✓    | Minimum or recommended hardware resources required for execution.                             |
| `software_requirements` | `JSON object`   |          | Required software, runtime, drivers, or platform dependencies.                                |
| `dataspace_requirements`| `JSON object`   |          | Required dataspace connectors, contract negotiations, and contact information                 |

## Semantic Model

The schema of the semantic model in the metadata is defined at [https://github.com/rox-architecture/RODEOS](https://github.com/rox-architecture/RODEOS). In the link, the automatic semantic model generation is also described.

## Requirement Expression

There three types of requirements in the metadata:

- **hardware** – physical and computational resources, such as sensors, hardware, memory, GPU, and disk capacity.
- **software** – software components and runtime capabilities, including installed tools, APIs, services, network connectivity, ports, and filesystem access.
- **dataspace** – requirements related to dataspace interactions, including connectors, contract negotiation, usage policies, and publishing permissions.

Requirements are described using a small domain specific language.
All requirements in the same list are conjunctive, meaning that every requirement must be satisfied.

## Requirement Expression Language Grammar

For now, the requirement language supports the following expressions:

| Expression         | Description                                                                   |
| ------------------ | ----------------------------------------------------------------------------- |
| `requires(x)`      | The specified resource, API, service, or interface must be available for use. |
| `x = value`        | The specified property must have the exact value.                             |
| `x >= value`       | The specified property must meet the minimum value.                           |
| `x <= value`       | The specified property must not exceed the maximum value.                     |
| `x in {a, b, ...}` | The specified property must match one of the listed values.                   |

A quick example:

```text
requires(kubernetes.api)
memory >= 8 GB
cpu.architecture in {amd64, arm64}
```

Notice that we use namespaces to describe the value more intuitively, e.g., `kubernetes.api`.
Combined with the grammar, we can express something like:

```
requires(dataspace.connector.dlr)
requires(docker)
requires(kubernetes.api)
requires(hardware.sensor.camera)

hardware.sensor.camera.type = depth
hardware.sensor.camera.frame_rate >= 30 Hz

software.runtime.python >= 3.12
```

## Namespaces

Currently, users can flexibly extend the namespace to add more details.
Below shows suggested namespaces for each requirement type `hardware`, `software`, and `dataspace`.

```
hardware
├── compute
│   ├── cpu
│   ├── memory
│   ├── gpu
├── robot
├── end_effector
├── sensor
│   ├── camera
│   ├── lidar
│   ├── radar
│   ├── imu
│   ├── force_torque
│   ├── proximity
│   └── encoder
└── interface
    ├── usb
    ├── ethernet
    ├── serial
    ├── i2c
    └── gpio

software
├── os
├── runtime
├── framework
├── middleware
├── api
├── service
├── network
├── filesystem
├── package
└── permission

dataspace
├── adapter
├── connector
├── provider
├── asset
├── contract
├── negotiation
├── policy
├── transfer
└── permission
```

## Examples

### Hardware Requirements


```text
requires(hardware.robot)
```

A robot must be present in the execution environment.

```text
hardware.robot.model = ur5e
```

The required robot model is a UR5e.

```text
requires(hardware.end_effector)
hardware.end_effector.type = parallel_gripper
```

A parallel gripper must be available as an end effector.

```text
hardware.end_effector.payload >= 5 kg
```

The end effector must support a payload of at least 5 kg.

```text
requires(hardware.sensor.camera)
hardware.sensor.camera.type = depth
```

A depth camera must be available.

```text
hardware.sensor.camera.frame_rate >= 30 Hz
```

The camera must provide a frame rate of at least 30 Hz.

```text
requires(hardware.sensor.lidar)
hardware.sensor.lidar.range >= 50 m
```

A LiDAR sensor with a range of at least 50 m must be available.

```text
hardware.compute.cpu.architecture in {amd64, arm64}
```

The CPU architecture must be either AMD64 or ARM64.

```text
hardware.compute.memory >= 8 GB
```

At least 8 GB of system memory is required.

```text
requires(hardware.interface.usb)
hardware.interface.usb.version >= 3.0
```

A USB interface supporting version 3.0 or newer is required.

---

### Software Requirements

```text
requires(software.runtime.docker)
```

A usable Docker runtime is required.

```text
requires(software.api.docker)
```

Access to the Docker API is required.

```text
requires(software.api.kubernetes)
```

Access to a Kubernetes API is required.

```text
requires(software.package.kubernetes_python_client)
```

The Kubernetes Python client package must be installed.

```text
software.runtime.python >= 3.12
```

Python 3.12 or newer is required.

```text
software.os.name = linux
```

The workflow must run on Linux.

```text
requires(software.middleware.ros2)
software.middleware.ros2.distro in {humble, jazzy}
```

ROS 2 Humble or Jazzy is required.

```text
requires(software.middleware.ros2.topic./camera/image_raw)
```

The ROS 2 topic `/camera/image_raw` must be available.

```text
requires(software.service.container_registry.localhost:5000)
```

A container registry must be available at `localhost:5000`.

```text
requires(software.network.tcp.port.8080)
```

TCP port 8080 must be available for use.

---

### Dataspace Requirements

```text
requires(dataspace.connector)
```

A usable dataspace connector is required.

```text
requires(dataspace.connector.dlr)
```

The DLR dataspace connector is required.

```text
dataspace.connector.type = edc
```

The connector must be based on EDC.

```text
requires(dataspace.adapter.tractusx)
```

A Tractus-X-compatible dataspace adapter is required.

```text
requires(dataspace.provider)
dataspace.provider.bpn = BPNL000000000001
```

Access to the specified dataspace provider is required.

```text
requires(dataspace.asset)
dataspace.asset.id = asset-123
```

The asset identified as `asset-123` must be available.

```text
dataspace.asset.type = file
```

The required dataspace asset must be a file asset.

```text
requires(dataspace.contract)
dataspace.contract.status = active
```

An active contract must be available.

```text
requires(dataspace.negotiation)
dataspace.negotiation.status = finalized
```

A successfully finalized contract negotiation is required.

```text
requires(dataspace.permission.publish)
```

Permission to publish an asset to the dataspace is required.
