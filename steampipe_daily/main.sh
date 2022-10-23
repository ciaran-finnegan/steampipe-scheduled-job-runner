#!/bin/bash
#                 STEAMPIPE DAILY JOB
# #################################################################################
# Description  = Steampipe daily job and export results to an S3 bucket in json & html format.
# version      = "0.1"
# maintainer   = "https://github.com/ciaran-finnegan"
# status       = "Development"
# #################################################################################

banner()
{
  echo "+------------------------------------------------------------------------+"
  printf "| %-90s |\n" "`date`"
  echo "|         |"
  printf "| %-80s |\n" "$@"
  echo "+------------------------------------------------------------------------+"
}

# Clone the steampipe module to current directory /workspace (must be empty)
# Group not required for Github (useful for Gitlab groups)
# group=""
repo="steampipe-security-controls-module"

# Change these for your environment
git config --global user.email "email"
git config --global user.name "name"
git clone --depth 1 https://dummyuser:$GITHUB_PROJECT_ACCESS_TOKEN@github.com/ciaran-finnegan/$repo /workspace/$repo/

# Configure the steampipe plugins
echo -e $STEAMPIPE_PLUGIN_CONFIG_OKTA > ~/.steampipe/config/okta.spc
echo -e $STEAMPIPE_PLUGIN_CONFIG_CROWDSTRIKE > ~/.steampipe/config/crowdstrike.spc
echo -e $STEAMPIPE_PLUGIN_CONFIG_SALESFORCE > ~/.steampipe/config/salesforce.spc
echo -e $STEAMPIPE_PLUGIN_CONFIG_NET > ~/.steampipe/config/net.spc
echo -e $STEAMPIPE_PLUGIN_CONFIG_CSV > ~/.steampipe/config/csv.spc

# Create a variable with todays date to name the steampipe check output file
today=$(date +"%Y-%m-%d_%I-%M-%S")
json_filename="${today}_steampipe-check-all-output.json"
html_filename="${today}_steampipe-check-all-output.html"

# Run steampipe benchmark and export results in json and html format, redirect STDOUT to /dev/null to avoid congesting Cloudwatch logs
banner "Running steampipe service."
steampipe check all --theme=plain --progress=false --export=$json_filename --export=$html_filename  > /dev/null

aws s3 cp $repo/$MARKDOWN s3://$SCHEDULEDJOBREPORTS_NAME

cd ..

# Copy the output file to S3
aws s3 cp $repo/$json_filename s3://$SCHEDULEDJOBREPORTS_NAME
aws s3 cp $repo/$html_filename s3://$SCHEDULEDJOBREPORTS_NAME

echo "Copied $json_filename  & $html_filename to s3://$SCHEDULEDJOBREPORTS_NAME"

banner "Steampipe job completed"
