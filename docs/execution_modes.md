# Execution Mode Configurations

The execution can have several configurations.

Use the endpoint `POST /config` to configure the execution modes. See [request body](./../src/cee/schema/api_schema.py).

## Automatic Negotiation

Boolean

| Value | Effect |
| --- | --- |
| True | automatically negotiate the node with no negotiation |
| False | workflow will terminate in the middle, when encountered a non-negotiated node |
