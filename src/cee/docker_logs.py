import docker

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse


router = APIRouter(
    prefix="/system/logs",
    tags=["Docker Logs"],
)


LOG_CONTAINERS = {
    "api": "kit-backend-api",
    "worker-1": "kit-worker-1",
    "worker-2": "kit-worker-2",
    "worker-3": "kit-worker-3",
    "worker-4": "kit-worker-4",
}


def get_docker_client():
    return docker.from_env()


@router.get("/{service}/stream")
async def stream_container_logs(service: str):
    container_name = LOG_CONTAINERS.get(service)

    if container_name is None:
        raise HTTPException(
            status_code=404,
            detail="Unknown service",
        )

    try:
        docker_client = get_docker_client()

        container = docker_client.containers.get(
            container_name
        )

    except docker.errors.NotFound:
        raise HTTPException(
            status_code=404,
            detail=f"Container '{container_name}' not found",
        )

    except docker.errors.DockerException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Docker error: {str(e)}",
        )

    def generate():
        try:
            for line in container.logs(
                stream=True,
                follow=True,
                tail=200,
                timestamps=True,
            ):
                text = line.decode(
                    "utf-8",
                    errors="replace",
                ).rstrip()

                yield f"data: {text}\n\n"

        except docker.errors.DockerException as e:
            yield (
                f"data: Docker error: "
                f"{str(e)}\n\n"
            )

        finally:
            docker_client.close()

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )