# Accessing DB Console

```
psql -U postgres -d workflowdb
```

In the container:

```
docker exec -it canvas-execution-db psql -U admin -d workflowdb
```

## Checking DB

To see the tables
```
\dt
```

To see the contents
```
SELECT * FROM workflows;
```

## DBeaver