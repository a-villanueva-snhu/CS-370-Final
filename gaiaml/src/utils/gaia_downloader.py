# A simple downloader for fetching Gaia DR3 data from 
# ESA's Gaia Archive using native astroquery capabilities.

import sqlite3
from astroquery.gaia import Gaia
from logs import logger
from data.database.sqlite import db as db
from config import config_manager


def _table_has_rows(table_name):
    try:
        return len(db.fetch_data(table_name, limit=1)) > 0
    except sqlite3.Error:
        return False

def download_gaia_dr3_data():
    """
    Downloads Gaia DR3 data from ESA's Gaia Archive natively.
    """
    query = """
    SELECT TOP 100
        source_id,
        ra,
        dec,
        parallax,
        phot_g_mean_mag,
        phot_bp_mean_mag,
        phot_rp_mean_mag
    FROM gaiadr3.gaia_source
    """

    logger.log_info("Starting Gaia DR3 data download...")

    try:
        # NATIVE: Use launch_job_async to prevent server-side timeouts
        job = Gaia.launch_job_async(query)
        
        # NATIVE: get_results() returns an Astropy Table object
        results = job.get_results()

        # Keep the download columns aligned with the gaia_dr3_data table schema.
        df = results.to_pandas()
        model_relevant_cols = [
            'source_id', 'ra', 'dec', 'parallax',
            'phot_g_mean_mag', 'phot_bp_mean_mag', 'phot_rp_mean_mag'
        ]
        df = df[model_relevant_cols]
        
        # Insert natively into SQLite (replaces custom db handler)
        with sqlite3.connect(config_manager.get_config_value('database_settings', 'database_file_path')) as conn:
            df.to_sql('gaia_dr3_data', conn, if_exists='append', index=False)
            
        logger.log_info(f"Gaia DR3 data downloaded and inserted into the database. Rows: {len(df)}")

        # NATIVE CSV STORAGE ALTERNATIVE:
        # If your goal was just to fetch a CSV file directly without memory overhead, 
        # astroquery can bypass python entirely natively:
        # Gaia.launch_job_async(query, dump_to_file=True, output_format='csv', output_file='gaia_dr3_data.csv')

    except Exception as e:
        logger.log_error(f"Error fetching/inserting Gaia DR3 data: {e}")


def download_test_data(force_refresh=False):
    """
    Downloads a small test dataset to see the Gaia DR3 data structure and test the database insertion.
    """
    if not force_refresh and _table_has_rows('test_data'):
        logger.log_info("Using cached test_data rows. Skipping remote Gaia download.")
        return

    query = """
    SELECT TOP 10
        gs.source_id,
        gs.ra,
        gs.dec,
        gs.parallax,
        gs.phot_g_mean_mag,
        gs.phot_bp_mean_mag,
        gs.phot_rp_mean_mag
    FROM gaiadr3.vari_planetary_transit AS vpt
    JOIN gaiadr3.gaia_source AS gs
        ON vpt.source_id = gs.source_id
    """

    logger.log_info("Downloading test data with confirmed exoplanets from Gaia DR3...")

    db_path = config_manager.get_config_value('database_settings', 'database_file_path')

    try:
        # For a tiny sample query, synchronous execution avoids async job queue overhead.
        job = Gaia.launch_job(query)
        results = job.get_results()
        
        # NATIVE COLUMN TRIMMING:
        # The ADQL query above already restricts the columns natively, but if you need to 
        # filter a larger result set programmatically in Python, use Astropy's native column indexing:
        model_relevant_cols = [
            'source_id', 'ra', 'dec', 'parallax', 'phot_g_mean_mag', 
            'phot_bp_mean_mag', 'phot_rp_mean_mag'
        ]
        results = results[model_relevant_cols] 

        # NATIVE DATABASE STORAGE:
        df = results.to_pandas()
        with sqlite3.connect(db_path) as conn:
            df.to_sql('test_data', conn, if_exists='replace', index=False)
            
        logger.log_info(f"Test data downloaded and inserted into the database. Rows: {len(df)} Path: {db_path}")
        
    except Exception as e:
        logger.log_error(f"Error downloading test data from Gaia DR3: {e}")
        