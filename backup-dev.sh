echo "backup workflow"
curl http://10.68.35.21:9000/api/metadata/workflow > workflows.json
echo "backup task"
curl http://10.68.35.21:9000/api/metadata/taskdefs > tasks.json
