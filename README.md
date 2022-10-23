# steampipe-scheduled-job-runner
Run scheduled Steampipe benchmark checks securely and inexpensively on AWS using ECS Fargate. We use AWS Copilot to define Step Functions and AWS ECS Fargate scheduled jobs to run steampipe checks in docker. Steampipe benchmarks and controls are retrieved at run-time from a git respository to support a [GitOps workflow](https://about.gitlab.com/topics/gitops/)

## Steampipe Scheduled Job
This job runs a scheduled steampipe check command, results are written in .json and .html formats to an AWS S3 bucket.

## Prerequisites
Basic familiarity with the following tools and services is recommended.

-   Steampipe, https://steampipe.io
-   AWS Copilot, https://docs.aws.amazon.com/AmazonECS/latest/developerguide/getting-started-aws-copilot-cli.html
-   AWS, https://aws.amazon.com
-   Git, https://www.w3schools.com/git/default.asp
-   Docker, https://www.docker.com/101-tutorial/
-   Bash shell scripting, https://www.w3schools.io/terminal/bash-tutorials/

You will need the following
- An AWS account that you can access using the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- A steampipe benchmark, control or steampipe module, more [here](https://steampipe.io/docs/reference/mod-resources/benchmark)
- A Git repository to store your Steampipe benchmark or control checks, e.g. [Steampipe module ](https://github.com/ciaran-finnegan/steampipe-security-controls-module)
- Steampipe configuration files for the [Steampipe plugins](https://hub.steampipe.io/plugins) used by your module, benchmark or controls
  

# Installation

## Configure CLI access to the AWS Account

Refer to the AWS CLI [documentation](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) to complete this step, 

You can verify this by issuing the following AWS CLI command

```aws s3 ls```
or
```aws s3 ls --profile my-profile-name```
if you are using AWS CLI configuration profiles


## Installing and configuring AWS Co-pilot
Follow the instructions [here](https://aws.github.io/copilot-cli/docs/overview/) to install and configure AWS Co-pilot. you can verify Co-pilot is installed and configured correctly by following the instructions [here](https://aws.github.io/copilot-cli/docs/getting-started/verify/).

If you are using AWS CLI configuration profiles you will need to export the applicable configuration profile to your shell environment as an environment variable e.g.

```export AWS_PROFILE=my-profile-name```

## AWS Copilot configuration

Clone this repository and make it your active directory

```
git clone https://github.com/ciaran-finnegan/steampipe-scheduled-job-runner.git
cd steampipe-scheduled-job-runner
```


### Initialize Application and Job.
```
copilot init
```
Application name: my-job-runner
Workload type: Scheduled Job
Job name: steampipe-daily
Dockerfile: Dockerfile
Schedule type: Fixed Schedule
Fixed schedule: Daily

### Initialize Environment
```
copilot env init
```
Environment name: e.g. development, staging or production
Credential source: e.g. [profile my-profile-name]
Default environment configuration? Yes, use default.

### Deploy your environment.

```
copilot env deploy --name development
```

### Redeploying after a configuration change

```
copilot deploy
```

## Adding secrets as AWS Systems Manager Parameter Store SecureString parameters


Follow the instructions [here](https://aws.github.io/copilot-cli/docs/commands/secret-init/).

```
copilot secret init
```

e.g.
 ➜  mg-infosec-ecs-runners git:(production) ✗ copilot secret init              
Secret name:  baselinecreds
Test secret value:
Environment test is already on the latest version v1.9.0, skip upgrade.
...Put secret baselinecreds to environment test
✔ Successfully put secret baselinecreds in environment test as /copilot/mg-infosec-job-runner/test/secrets/baselinecreds.
You can refer to these secrets from your manifest file by editing the `secrets` section.
`secrets:
    baselinecreds: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/baselinecreds`

## Testing

Logon to the AWS console with administrative privileges and select Step Functions, State Machines
Choose the mg-infosec-job-runner-test-owasp-zap-daily state machine
Choose Start Execution

Browse to Cloudwatch Log Groups
Choose the /copilot/mg-infosec-job-runner-test-owasp-zap-daily log group
Open the latest states log group to review task states
Open the latest copilot/owasp-zap-daily log group to review the status of the owasp-zap job

## Delete Application (Do not run delete unless agreed across the team.)
WARN: Copilot environment and application are shared (similar to $terraform workspace). So, if you delete application or enviroment from local terminal, copilot would delete the cloudformation ECS stack shared across the team.
```
copilot app delete mg-infosec-job-runner
```
# Issues

1) AWS secrets manager with customer managed keys (CMKs) is preferred to AWS systems manager parameter store to correctly restrict access to secrets.
2) Fargate spot instances could be used to further reduce run costs
3) Documentation requires improvement

