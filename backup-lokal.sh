echo "backup workflow"
curl http://localhost:8080/api/metadata/workflow > workflow-optimize.json
echo "backup task"
curl http://localhost:8080/api/metadata/taskdefs > task-optimize.json
