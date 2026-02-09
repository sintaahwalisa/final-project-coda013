from datetime import date

# Get current date and time
now = date.today()

# Connect to a data source

import great_expectations as gx
import os

# context_jan = gx.get_context(context_root_dir='./gx/')
context_jan = gx.get_context(context_root_dir='/opt/airflow/scripts/gx')

# Give a name to a Datasource. This name must be unique between Datasources.
datasource_name = f'expectation-1_{now}'
# datasource = context_jan.sources.add_pandas(datasource_name)
datasource = context_jan.sources.add_or_update_pandas(datasource_name)

# Give a name to a data asset
asset_name = f'transaction-1_{now}'
# path_to_data = 'data/processed/fact_transaction.csv'
path_to_data = '/opt/airflow/data/processed/fact_transaction.csv'

asset = datasource.add_csv_asset(asset_name, filepath_or_buffer=path_to_data)

# Build batch request
batch_request_feb = asset.build_batch_request()

# Create a checkpoint

checkpoint_2 = context_jan.add_or_update_checkpoint(
    name = f'checkpoint_2_{now}',
    batch_request = batch_request_feb,
    expectation_suite_name = 'expectation-transaction-dataset'
)

checkpoint_result = checkpoint_2.run()

# Build data docs

# context.build_data_docs()
context_jan.build_data_docs()

