"""
Load configuration parameters from files and environnement variables.
"""

from dotenv import dotenv_values


def get_config(application_name: str):
    """
    Load configuration parameters from files and environnement variables.

    Notes
    -----
    Default data is loaded from the '.env.default' file.
    It's updated from environement varaibles.
    If a variable is already in a previous
    file, it's overwritten. If a file does'nt exist, no exception is
    raised.

    Parameters
    ------
    None

    Retunrs
    ------
    dict
        The dictionnary with the parameters to use.
    """
    if not isinstance(application_name, str):
        raise TypeError()

    return {
        **dotenv_values("./config/.env.default"),
        **dotenv_values(f"./config/.env.{application_name}")
    }
