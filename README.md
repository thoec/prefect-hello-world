## Setup
Register Deployments and start a local Prefect server and work-pool by doing: 
* `hatch shell dev`
* `prefect server start &`
* `prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api`
* `prefect work-pool create local-work-pool --type process`
* `prefect --no-prompt deploy --prefect-file prefect.yaml --all`
* `prefect worker start --pool local-work-pool`

## Run
Trigger a run of the `hello-world`-deployment. This will in turn trigger multiple other runs of the `hello-world*` deployments. The trigger of hello-world3 will fail. Look for the:
`prefect.server.utilities.messaging.memory - Message failed after 4 retries and will be moved to the dead letter queue`
in the logs from the worker.
