from __future__ import division, absolute_import, print_function
from airflow.plugins_manager import AirflowPlugin

import operators
import helpers

# Defining the custom plugin class for Airflow
class AirflowRedshiftPlugin(AirflowPlugin):  # ✅ Changed from UdacityPlugin
    name = "aws_redshift_plugin"  # ✅ Renamed plugin for uniqueness
    operators = [
        operators.CreateTableOperator,
        operators.StageToRedshiftOperator,
        operators.LoadFactOperator,
        operators.LoadDimensionOperator,
        operators.DataQualityOperator
    ]
    helpers = [
        helpers.SqlQueries
    ]
