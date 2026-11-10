
curl -X POST http://localhost:8080/api/metadata/taskdefs \
      -H "Content-Type: application/json" \
      -d @tasks-dev.json

curl -X PUT http://localhost:8080/api/metadata/workflow \
     -H "Content-Type: application/json" \
     -d @workflow-optimize.json

