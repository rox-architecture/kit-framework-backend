from psycopg_pool import ConnectionPool
from psycopg.types.json import Jsonb
from datetime import datetime, UTC

pool = ConnectionPool(
    conninfo=(
        "host=localhost "
        "port=5432 "
        "dbname=workflowdb "
        "user=admin "
        "password=admin"
    )
)

class DbHandlerWorkflow():
    def insert_workflow(self, name:str, graph:dict, execution_flow:list):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO workflows (
                        workflow_name,
                        graph_json,
                        execution_flow
                    )
                    VALUES (%s, %s, %s)
                    RETURNING workflow_id, updated_at;
                    """,
                    (
                        name,
                        Jsonb(graph),
                        Jsonb(execution_flow),
                    ),
                )

                workflow_id, updated_at = cur.fetchone()

        return {
            "workflow_id": str(workflow_id),
            "updated_at": updated_at,
        }
    
    def delete_workflow(self, workflow_id:str):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM workflows
                    WHERE workflow_id = %s
                    RETURNING workflow_id;
                    """,
                    (workflow_id,),
                )

                deleted = cur.fetchone()

        if deleted is None:
            return False

        return True

    def get_workflow(self, workflow_id: str):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        workflow_id,
                        workflow_name,
                        graph_json,
                        execution_flow,
                        updated_at
                    FROM workflows
                    WHERE workflow_id = %s;
                    """,
                    (workflow_id,),
                )

                row = cur.fetchone()

        if row is None:
            return None

        return {
            "workflow_id": str(row[0]),
            "workflow_name": row[1],
            "graph_json": row[2],
            "execution_flow": row[3],
            "updated_at": row[4],
        }

    def get_all(self):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        workflow_id,
                        workflow_name,
                        updated_at,
                        graph_json,
                        execution_flow
                    FROM workflows
                    ORDER BY updated_at DESC;
                    """
                )

                rows = cur.fetchall()

        return [
            {
                "workflow_id": str(row[0]),
                "workflow_name": row[1],
                "updated_at": row[2],
                "graph_json": row[3],
                "execution_flow": row[4],
            }
            for row in rows
        ]


class DbHandlerExecution():

    def insert_execution(self, workflow_id: str):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO executions (
                        workflow_id,
                        current_state
                    )
                    VALUES (%s, %s)
                    RETURNING reference_id;
                    """,
                    (
                        workflow_id,
                        "PENDING",
                    ),
                )

                reference_id = cur.fetchone()[0]

            conn.commit()

        return {
            "reference_id": str(reference_id)
        }


    def get_execution(self, reference_id: str):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        reference_id,
                        workflow_id,
                        start_at,
                        finish_at,
                        current_state
                    FROM executions
                    WHERE reference_id = %s;
                    """,
                    (reference_id,),
                )

                row = cur.fetchone()

        if row is None:
            return None

        return {
            "reference_id": str(row[0]),
            "workflow_id": row[1],
            "start_at": row[2],
            "finish_at": row[3],
            "current_state": row[4],
        }


    def get_executions_by_workflow_id(self, workflow_id: str):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        reference_id,
                        workflow_id,
                        start_at,
                        finish_at,
                        current_state
                    FROM executions
                    WHERE workflow_id = %s
                    ORDER BY start_at DESC NULLS LAST;
                    """,
                    (workflow_id,),
                )

                rows = cur.fetchall()

        return [
            {
                "reference_id": str(row[0]),
                "workflow_id": row[1],
                "start_at": row[2],
                "finish_at": row[3],
                "current_state": row[4],
            }
            for row in rows
        ]


    def get_all_executions(self):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        reference_id,
                        workflow_id,
                        start_at,
                        finish_at,
                        current_state
                    FROM executions
                    ORDER BY start_at DESC NULLS LAST;
                    """
                )

                rows = cur.fetchall()

        return [
            {
                "reference_id": str(row[0]),
                "workflow_id": row[1],
                "start_at": row[2],
                "finish_at": row[3],
                "current_state": row[4],
            }
            for row in rows
        ]
    
    def get_executions_by_status(self, current_state: str):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        reference_id,
                        workflow_id,
                        start_at,
                        finish_at,
                        current_state
                    FROM executions
                    WHERE current_state = %s
                    ORDER BY start_at DESC NULLS LAST;
                    """,
                    (current_state,),
                )

                rows = cur.fetchall()

        return [
            {
                "reference_id": str(row[0]),
                "workflow_id": row[1],
                "start_at": row[2],
                "finish_at": row[3],
                "current_state": row[4],
            }
            for row in rows
        ]

    def execution_cancelled(self, reference_id: str):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE executions
                    SET
                        finish_at = %s,
                        current_state = 'CANCELLED'
                    WHERE reference_id = %s
                    RETURNING reference_id;
                    """,
                    (
                        datetime.now(UTC),
                        reference_id,
                    ),
                )

                row = cur.fetchone()

            conn.commit()

        return row is not None
       

    def execution_started(self, reference_id: str):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE executions
                    SET
                        start_at = %s,
                        current_state = 'RUNNING'
                    WHERE reference_id = %s
                    RETURNING reference_id;
                    """,
                    (
                        datetime.now(UTC),
                        reference_id,
                    ),
                )

                row = cur.fetchone()

            conn.commit()

        return row is not None

    def execution_finished(self, reference_id: str):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE executions
                    SET
                        finish_at = %s,
                        current_state = 'FINISHED'
                    WHERE reference_id = %s
                    RETURNING reference_id;
                    """,
                    (
                        datetime.now(UTC),
                        reference_id,
                    ),
                )
                row = cur.fetchone()

            conn.commit()

        return row is not None

    def execution_failed(self, reference_id: str):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE executions
                    SET
                        finish_at = %s,
                        current_state = 'FAILED'
                    WHERE reference_id = %s
                    RETURNING reference_id;
                    """,
                    (
                        datetime.now(UTC),
                        reference_id,
                    ),
                )
                row = cur.fetchone()

            conn.commit()

        return row is not None

    def reset(self):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    TRUNCATE TABLE executions;
                    """
                )

            conn.commit()