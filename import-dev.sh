
curl -X POST http://10.68.35.21:9000/api/metadata/taskdefs \
      -H "Content-Type: application/json" \
      -d @tasks.json

curl -X PUT http://10.68.35.21:9000/api/metadata/workflow \
     -H "Content-Type: application/json" \
     -d @workflow-dev.json

