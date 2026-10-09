echo "backup workflow"
curl http://10.14.159.142:30505/api/metadata/workflow > workflow-s.json
echo "backup task"
curl http://10.14.159.142:30505/api/metadata/taskdefs > task-s.json
