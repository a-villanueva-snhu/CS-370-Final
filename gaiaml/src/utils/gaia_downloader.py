# A simple downloader for fetching Gaia DR3 data from 
# ESA's Gaia Archive using native astroquery capabilities.

import sqlite3
from astroquery.gaia import Gaia
from logs import logger

def download_gaia_dr3_data():
    """
    Downloads Gaia DR3 data from ESA's Gaia Archive natively.
    """
    query = """
    SELECT TOP 100 *
    FROM gaiadr3.gaia_source
    """

    logger.log_info("Starting Gaia DR3 data download...")

    try:
        # NATIVE: Use launch_job_async to prevent server-side timeouts
        job = Gaia.launch_job_async(query)
        
        # NATIVE: get_results() returns an Astropy Table object
        results = job.get_results()

        # NATIVE DATABASE STORAGE: 
        # Convert Astropy Table to a Pandas DataFrame and use built-in SQL handling
        df = results.to_pandas()
        
        # Insert natively into SQLite (replaces custom db handler)
        with sqlite3.connect('gaia_data.db') as conn:
            df.to_sql('gaia_dr3_data', conn, if_exists='append', index=False)
            
        logger.log_info("Gaia DR3 data downloaded and inserted into the database.")

        # NATIVE CSV STORAGE ALTERNATIVE:
        # If your goal was just to fetch a CSV file directly without memory overhead, 
        # astroquery can bypass python entirely natively:
        # Gaia.launch_job_async(query, dump_to_file=True, output_format='csv', output_file='gaia_dr3_data.csv')

    except Exception as e:
        logger.log_error(f"Error fetching/inserting Gaia DR3 data: {e}")


def download_test_data():
    """
    Downloads a small test dataset to see the Gaia DR3 data structure and test the database insertion.
    """
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

    try:
        # NATIVE: Async execution
        job = Gaia.launch_job_async(query)
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
        with sqlite3.connect('gaia_data.db') as conn:
            df.to_sql('test_data', conn, if_exists='replace', index=False)
            
        logger.log_info("Test data downloaded and inserted into the database.")
        
    except Exception as e:
        logger.log_error(f"Error downloading test data from Gaia DR3: {e}")