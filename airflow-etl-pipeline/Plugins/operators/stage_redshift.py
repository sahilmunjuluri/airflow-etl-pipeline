from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 aws_credentials_id="",
                 table_name="",
                 s3_bucket="",
                 s3_key="",
                 file_format="JSON",
                 json_path="auto",
                 region="us-west-2",
                 *args, **kwargs):

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.aws_credentials_id = aws_credentials_id
        self.table_name = table_name
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.file_format = file_format
        self.json_path = json_path
        self.region = region

    def execute(self, context):
        redshift_hook = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        self.log.info(f"Staging data from S3 to Redshift: {self.s3_bucket}/{self.s3_key} → {self.table_name}")

        # Building the COPY command
        copy_sql = f"""
            COPY {self.table_name}
            FROM 's3://{self.s3_bucket}/{self.s3_key}'
            CREDENTIALS 'aws_iam_role={self.aws_credentials_id}'
            REGION '{self.region}'
        """

        if self.file_format.upper() == "JSON":
            copy_sql += f" FORMAT AS JSON '{self.json_path}';"
        elif self.file_format.upper() == "CSV":
            copy_sql += " FORMAT AS CSV IGNOREHEADER 1;"

        self.log.info(f"Executing COPY command: {copy_sql}")
        redshift_hook.run(copy_sql)

        self.log.info(f"Data staged successfully into {self.table_name}.")
