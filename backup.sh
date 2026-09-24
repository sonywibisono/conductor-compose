echo "backup workflow"
curl http://10.98.9.61:30504/api/metadata/workflow > workflows.json
echo "backup task"
curl http://10.98.9.61:30504/api/metadata/taskdefs > tasks.json
