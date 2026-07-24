# A simple downloader for fetching Gaia DR3 data from 
# ESA's Gaia Archive.

import astroquery
from astroquery.gaia import Gaia


def download_gaia_dr3_data():
    """
    Downloads Gaia DR3 data from ESA's Gaia Archive.
    This function uses the astroquery library to fetch the data.
    """

    # Define the query to fetch Gaia DR3 data 
    # Downloads a random smaple of 1000 rows from the Gaia DR3 source table.
    query = """
    SELECT TOP 1000 *
    FROM gaiadr3.gaia_source
    """

    # Execute the query and download the data
    job = Gaia.launch_job(query)
    results = job.get_results()

    # Save the results to a CSV file
    ## TODO: Replace this with the sqlite database storage method once implemented.
    results.write("gaia_dr3_data.csv", format="csv", overwrite=True)

    cleanup_conn()  # Clean up the connection to the Gaia Archive after downloading data

def download_test_data():
    """
    Downloads a small test dataset with confirmed exoplanets from Gaia DR3.
    This function is intended for testing purposes and uses a predefined query.
    """

    # Define the query to fetch a small test dataset
    #
    # Accesses the vari_planetary_transit table to get a small sample of stars with confirmed exoplanets.
    #
    ## phot_g_mean_mag < 15 and parallax > 10 are arbitrary filters to get a small sample of stars.
    query = """
    SELECT TOP 100 *
    FROM gaiadr3.vari_planetary_transit
    WHERE source_id IN (
        SELECT source_id
        FROM gaiadr3.gaia_source
        WHERE phot_g_mean_mag < 15
        AND parallax > 10
    )
    """

    # Execute the query and download the data
    job = Gaia.launch_job(query)
    results = job.get_results()

    # Save the results to a CSV file
    ## TODO: Replace this with the sqlite database storage method once implemented.
    results.write("gaia_test_data.csv", format="csv", overwrite=True)

    cleanup_conn()  # Clean up the connection to the Gaia Archive after downloading test data

def cleanup_conn():
    """
    Cleans up the connection to the Gaia Archive.
    This function should be called after all data downloads are complete.
    """

    # Close the connection to the Gaia Archive
    Gaia.close()