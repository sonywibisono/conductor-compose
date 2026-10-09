
curl -X POST http://localhost:8080/api/metadata/taskdefs \
      -H "Content-Type: application/json" \
      -d @task-fork.json

curl -X PUT http://localhost:8080/api/metadata/workflow \
     -H "Content-Type: application/json" \
     -d @workflow-forks.json

