## A simple downloader for fetching data from NASA's 
# Exoplanet Archive API. It is used to download data for 
# training and testing the model against known data.

import pandas as pd
import pyvo

## Execute the search and convert to a Pandas DataFrame
def download_nasaea_data():
    """
    Downloads data from NASA's Exoplanet Archive using the ADL query.
    Returns a Pandas DataFrame containing the results.
    """

    ## Connect to the TAP endpoint of NASA's Exoplanet Archive
    tap_url = "https://exoplanetarchive.ipac.caltech.edu/TAP"
    service = pyvo.dal.TAPService(tap_url)

    ## Write ADL query
    adl_query = """
    SELECT TOP 10 pl_name, pl_orbper, pl_rade, pl_bmasse, st_teff, st_rad
    FROM ps
    WHERE pl_orbper IS NOT NULL AND pl_rade IS NOT NULL AND pl_bmasse IS NOT NULL
    """

    # Execute the query
    result = service.search(adl_query)

    # Convert to a Pandas DataFrame
    df = result.to_table().to_pandas()

    # Save the results to a CSV file
    # TODO: Convert to save to sqlite database once implemented.
    df.to_csv("nasa_exoplanet_data.csv", index=False)

    ## Cleanup
    # Close connection to the TAP service
    service.close()

    return df