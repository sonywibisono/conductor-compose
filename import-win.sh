
curl -X POST http://10.14.68.179:8080/api/metadata/taskdefs \
      -H "Content-Type: application/json" \
      -d @tasks.json

curl -X PUT http://10.14.68.179:8080/api/metadata/workflow \
     -H "Content-Type: application/json" \
     -d @workflows.json

