
curl -X POST http://10.14.159.142:30505/api/metadata/taskdefs \
      -H "Content-Type: application/json" \
      -d @tasks.json

curl -X PUT http://10.14.159.142:30505/api/metadata/workflow \
     -H "Content-Type: application/json" \
     -d @workflows.json

