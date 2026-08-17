# A simple downloader for fetching Gaia DR3 data from 
# ESA's Gaia Archive using native astroquery capabilities.

import sqlite3
import os
import pandas as pd
from astroquery.gaia import Gaia
import logs.logger as logger
from config import config_manager
from data.database.sqlite import db as db


def _get_database_path() -> str:
    """Return a concrete SQLite path for strict typing and runtime safety."""
    default_path = os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')),
        'gaiaml.db'
    )
    db_path = config_manager.get_config_value('database_settings.database_file_path', default_path)
    if not isinstance(db_path, str):
        return default_path
    return db_path


def _table_row_count(table_name):
    try:
        return len(db.fetch_data(table_name, limit=-1))
    except sqlite3.Error:
        return 0

def download_gaia_dr3_data(count=100, force_refresh=False):
    """
    Downloads Gaia DR3 data from ESA's Gaia Archive natively.
    """
    query = f"""
    SELECT TOP {count}
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
        if results is None:
            logger.log_error("Gaia DR3 query returned no results.")
            return

        # Keep the download columns aligned with the gaia_dr3_data table schema.
        df: pd.DataFrame = results.to_pandas()
        model_relevant_cols = [
            'source_id', 'ra', 'dec', 'parallax',
            'phot_g_mean_mag', 'phot_bp_mean_mag', 'phot_rp_mean_mag'
        ]
        df = df[model_relevant_cols]
        
        # Insert natively into SQLite (replaces custom db handler)
        with sqlite3.connect(_get_database_path()) as conn:
            write_mode = 'replace' if force_refresh else 'append'
            df.to_sql('gaia_dr3_data', conn, if_exists=write_mode, index=False)
            
            logger.log_info(f"Gaia DR3 data downloaded and inserted into the database. Rows: {len(df)}")

        # NATIVE CSV STORAGE ALTERNATIVE:
        # If your goal was just to fetch a CSV file directly without memory overhead, 
        # astroquery can bypass python entirely natively:
        # Gaia.launch_job_async(query, dump_to_file=True, output_format='csv', output_file='gaia_dr3_data.csv')

    except Exception as e:
        logger.log_error(f"Error fetching/inserting Gaia DR3 data: {e}")


def download_confirmed_exoplanets_data(count=10, force_refresh=False):
    """
    Downloads a small confirmed exoplanets dataset from Gaia DR3 to test the database insertion.
    """
    existing_count = _table_row_count('confirmed_exoplanets_data')
    if not force_refresh and existing_count >= count:
        logger.log_info(
            f"Using cached confirmed_exoplanets_data rows ({existing_count}). "
            f"Requested {count}; skipping remote Gaia download."
        )
        return

    query = f"""
    SELECT TOP {count}
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

    db_path = _get_database_path()

    try:
        # For a tiny sample query, synchronous execution avoids async job queue overhead.
        job = Gaia.launch_job(query)
        results = job.get_results()
        if results is None:
            logger.log_error("Confirmed exoplanets query returned no results.")
            return
        
        # Keep columns aligned to model feature expectations and mark confirmed positives.
        df: pd.DataFrame = results.to_pandas()
        expected_cols = [
            'source_id', 'ra', 'dec', 'parallax',
            'phot_g_mean_mag', 'phot_bp_mean_mag', 'phot_rp_mean_mag'
        ]
        df = df[[col for col in expected_cols if col in df.columns]].copy()
        df['is_confirmed_host'] = 1

        with sqlite3.connect(db_path) as conn:
            # A larger request must replace the smaller cache; appending TOP N
            # results would duplicate the same leading rows.
            write_mode = 'replace' if force_refresh or existing_count < count else 'append'
            df.to_sql('confirmed_exoplanets_data', conn, if_exists=write_mode, index=False)
            
        logger.log_info(f"Confirmed exoplanets data downloaded and inserted into the database. Rows: {len(df)} Path: {db_path}")
        
    except Exception as e:
        logger.log_error(f"Error downloading confirmed exoplanets data from Gaia DR3: {e}")
        