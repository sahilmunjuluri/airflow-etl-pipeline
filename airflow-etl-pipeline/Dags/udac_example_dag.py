from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import (CreateTableOperator, StageToRedshiftOperator, LoadFactOperator,
                                LoadDimensionOperator, DataQualityOperator)
from helpers import SqlQueries
from sparkify_dimension_subdag import load_dimension_subdag
from airflow.operators.subdag_operator import SubDagOperator

# Configurable Variables
s3_bucket = 'my-redshift-bucket'  
song_s3_key = "song_data"
log_s3_key = "log_data"
log_json_file = "log_json_path.json"

default_args = {
    'owner': 'Sahil',  # 
    'depends_on_past': True,
    'start_date': datetime(2024, 2, 20),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'catchup': True
}

dag_name = 'aws_redshift_airflow_pipeline'  
dag = DAG(dag_name,
          default_args=default_args,
          description='ETL pipeline to load and transform data in Redshift with Airflow',
          schedule_interval='0 * * * *',
          max_active_runs=1          
        )

start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)

create_tables_in_redshift = CreateTableOperator(
    task_id='create_tables_in_redshift',
    redshift_conn_id='redshift',
    dag=dag
)

stage_events_to_redshift = StageToRedshiftOperator(
    task_id='Stage_events',
    table_name="staging_events",
    s3_bucket=s3_bucket,
    s3_key=log_s3_key,
    file_format="JSON",
    log_json_file=log_json_file,
    redshift_conn_id="redshift",
    aws_credential_id="aws_credentials",
    dag=dag,
    provide_context=True
)

stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Stage_songs',
    table_name="staging_songs",
    s3_bucket=s3_bucket,
    s3_key=song_s3_key,
    file_format="JSON",
    redshift_conn_id="redshift",
    aws_credential_id="aws_credentials",
    dag=dag,
    provide_context=True
)

load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    redshift_conn_id='redshift',
    sql_query=SqlQueries.songplay_table_insert, 
    dag=dag
)

load_user_dimension_table = SubDagOperator(
    subdag=load_dimension_subdag(
        parent_dag_name=dag_name,
        task_id="Load_user_dim_table",
        redshift_conn_id="redshift",
        start_date=default_args['start_date'],
        sql_statement=SqlQueries.user_table_insert,
        delete_load=True,
        table_name="users",
    ),
    task_id="Load_user_dim_table",
    dag=dag,
)

run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    dag=dag,
    redshift_conn_id="redshift",
    tables=["artists", "songplays", "songs", "time", "users"]
)

end_operator = DummyOperator(task_id='Stop_execution', dag=dag)

start_operator >> create_tables_in_redshift
create_tables_in_redshift >> [stage_songs_to_redshift, stage_events_to_redshift] >> load_songplays_table

load_songplays_table >> [load_user_dimension_table] >> run_quality_checks >> end_operator
