# this Airflow dag is to call Cloud function to create and Import dataset for AutoML - ETA training.
import json
import datetime
from airflow import DAG
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python_operator import PythonOperator
from airflow import models
from airflow.utils.dates import days_ago
# Importing the environment variables from config file
from airflow.models import Variable
# Google cloud operators
from airflow.providers.google.cloud.operators.functions import (
    CloudFunctionDeleteFunctionOperator,
    CloudFunctionDeployFunctionOperator,
    CloudFunctionInvokeFunctionOperator,
)

# Set the schedule time for pipeline sunday 1:30 AM UTC
schedule_interval = '30 1 * * 0'

default_args = {
    "owner": "med_team",
    "start_date": days_ago(1)
}
env_vars = Variable.get("TPM_ETA_VARS", deserialize_json=True)

dag_name = "med_cf_create_dataset"

#dag
dag = DAG(dag_name, default_args = default_args, schedule_interval = schedule_interval, tags = ['cloud_function', 'create_automl_dataset'],access_control = {"test_acc_control" : {"can_read", "can_edit"}})

payload = Variable.get("CF_PAYLOADS", deserialize_json = True)
payload = json.dumps(payload[0]['create_dataset'])



project_id = env_vars["project_id"]
#service account to connect GCP
gcp_conn_id = "sa-med-ml"
location = "us-central1"
# cloud function name
function_id = "cf_create_eta_automl_dataset"

invoke_cf = CloudFunctionInvokeFunctionOperator(
        task_id = "invoke_cf",
        project_id = project_id,
        location = location,
        gcp_conn_id = gcp_conn_id,
        input_data = {"data": payload},
        function_id = function_id,
        dag = dag
    )
 

email_to = "muthappan.ml@gmail.com"
subject = "Create dataset cloud function successfully initiated"
html_content = "<p> You have got mail! <p>"

success = EmailOperator(
    task_id = "success_mail", 
    to = email_to,
    subject = subject,
    html_content = html_content,
    dag = dag)

trigger_rule = "one_failed"
subject = "Error calling create dataset cloud function"
html_content = "<p> You have got mail! <p>"

error_email = EmailOperator(
        task_id = "error_email",
        trigger_rule = trigger_rule,
        to = email_to,
        subject = subject,
        html_content = html_content,
        dag = dag)

invoke_cf>>success
invoke_cf>>error_email
