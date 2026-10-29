
curl -X POST https://qrox.safnatelindo.com/api/metadata/taskdefs \
      -H "Content-Type: application/json" \
      -d @tasks.json

curl -X PUT https://qrox.safnatelindo.com/api/metadata/workflow \
     -H "Content-Type: application/json" \
     -d @workflows.json

