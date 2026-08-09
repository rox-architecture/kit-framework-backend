from typing import Any, Literal
from pydantic import BaseModel, HttpUrl
from cee.schema.execution_schema import Item
from cee.node_plugins.base import Base
import requests


class SendToUrl(Base):
    """Send binary data to a URL."""

    # Input is always a list of Items
    class InputSpec(BaseModel):
        pass

    # Output is always a list of Items
    class OutputSpec(BaseModel):
        pass

    class ParamSpec(BaseModel):
        """SendToUrl node param spec."""
        url: HttpUrl
        method: Literal[
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
        ] = "POST"
        timeout: float = 30.0

    def __init__(self, node: dict[str, Any]) -> None:
        """Initialize the instance."""
        super().__init__(node)

    def run(self, input_data: dict | None = None) -> None:
        """Run the node."""
        print(f"[Node {self.node_id}] Execution started")

        # get parameters
        url = str(self.params["url"])
        method = self.params["method"].upper()
        timeout = self.params["timeout"]

        request_kwargs: dict[str, Any] = {
            "method": method,
            "url": url,
            "timeout": timeout,
        }

        # GET and DELETE do not require input data.
        if method not in {"GET", "DELETE"}:
            validated_input = self.InputSpec.model_validate(input_data)
            item = validated_input.input_0

            content_type = (
                item.json_data.get("content_type")
                or "application/octet-stream"
            )

            request_kwargs["headers"] = {
                "Content-Type": str(content_type),
            }
            request_kwargs["data"] = item.binary

        # Send the requset
        response = requests.request(**request_kwargs)

        # Raise an exception for 4xx and 5xx responses.
        response.raise_for_status()

        # Extract the received response header content-type
        response_content_type = (
            response.headers.get("content-type")
            or "application/octet-stream"
        )

        # wrap into an Item object
        data = Item(
            json_data={
                "content_type": response_content_type,
                "content_length": len(response.content),
                "status_code": response.status_code,
            },
            binary=response.content,
        ).model_dump()

        # set 'data' as the output at port index 0
        self.set_output(port=0, item=data)
        self.finished = True