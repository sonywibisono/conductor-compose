
curl -X POST http://localhost:9090/api/metadata/taskdefs \
      -H "Content-Type: application/json" \
      -d @tasks.json

curl -X PUT http://localhost:9090/api/metadata/workflow \
     -H "Content-Type: application/json" \
     -d @workflows.json

