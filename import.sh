
curl -X POST http://127.0.0.1:8080/api/metadata/taskdefs \
     -H "Content-Type: application/json" \
     -d @tasks.json

curl -X PUT http://127.0.0.1:8080/api/metadata/workflow \
     -H "Content-Type: application/json" \
     -d @workflows.json

