## Request temporary AWS Access Token

```
okta
breakglass -a runcmd-security-dev
export AWS_PROFILE=runcmd-security-dev-bg
```

## Deploying via Copilot

Create a gitlab project access token for the gitlab.mantelgroup.com.au/infosec/security-reporting.git repo and create an environment variable, GITLAB_PROJECT_ACCESS_TOKEN in vars/.env for it


```
export $(grep -v '^#' vars/.env | xargs)
export AWS_PROFILE=runcmd-security-dev-bg
copilot init

Use existing application: Yes
Application name: job-runner
Workload type: Scheduled Job
Job name: steampipe-daily
Dockerfile: ./Dockerfile
Schedule type: Fixed Schedule
Fixed schedule: Daily
```

### Redeploying after a configuration change

```
export AWS_PROFILE=runcmd-security-dev-bg
copilot deploy
```
## Adding secrets as SSM Parameter Store SecureString parameters

The following secrets must be set;

-   GITLAB_PROJECT_ACCESS_TOKEN
-   STEAMPIPE_PLUGIN_CONFIG_OKTA
-   STEAMPIPE_PLUGIN_CONFIG_CROWDSTRIKE
-   STEAMPIPE_PLUGIN_CONFIG_SALESFORCE
-   STEAMPIPE_PLUGIN_CONFIG_NET
-   STEAMPIPE_PLUGIN_CONFIG_CSV
  
Follow the instructions at the URL below
https://aws.github.io/copilot-cli/docs/commands/secret-init/

### Note, we have not yet determined how to set multiline secrets via the copilot interface, these have been set manually in parameter store

```
copilot secret init
```

e.g.
 ➜  job-runners git:(production) ✗ copilot secret init              
Secret name:  baselinecreds
Test secret value: 
Environment test is already on the latest version v1.9.0, skip upgrade.
...Put secret baselinecreds to environment test
✔ Successfully put secret baselinecreds in environment test as /copilot/job-runner/test/secrets/baselinecreds.
You can refer to these secrets from your manifest file by editing the `secrets` section.
`secrets:
    baselinecreds: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/baselinecreds`

## Customising the steampipe benchmark report
The steampipe benchmark report output (steampipe check all) can be quite large (650Kb) as it contains detailed results of each individual check. These are not necessary for monthly reporting. Steampipe supports customiaation of reports via n Control Output Templates.

A custom template (custom.json) that omits the detailed results is copied to ~/.steampipe/check/templates as part of the docker image build. The custom report can be generated by referencing it 

```
steampipe check ... --export custom

```


 You will find the built-in  templates in ~/.steampipe/check/templates
There should be a directory there called json - this is the default template that is used when you export to json
Create another directory in ~/.steampipe/check/templates called custom.json
Copy the contents of json to custom.json
Open custom.json/output.tmpl
Remove Line 55 -  61
Now, you should be able to do steampipe check ... --export custom

 output to reduce size ## Creating an S3 bucket

```
copilot storage init -t S3
scheduled-job-reports
```

# To create a bucket named "my-bucket" accessible by the "api" service.
```
copilot storage init
S3
scheduled-job-reports
```

The bucket can be referenced in bash as SCHEDULEDJOBREPORTS_NAME