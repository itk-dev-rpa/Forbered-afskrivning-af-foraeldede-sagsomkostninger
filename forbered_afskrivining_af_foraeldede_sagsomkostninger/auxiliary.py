"""Module for support methods that could be reused in other parts of the library"""
import tempfile
import os
import atexit


class TemporaryFile:
    """Create a temporary named file, and automatically delete it.
    The file will automatically be deleted (at exit), even if an uncaught exception occurs.
    """
    def __init__(self):
        self.file = tempfile.NamedTemporaryFile(delete=False)  # pylint: disable=(consider-using-with)
        self.file.close()
        atexit.register(self.clean_up)

    def clean_up(self) -> None:
        """Delete the file"""
        os.remove(self.file.name)

    def __repr__(self) -> str:
        return self.file.name


def get_fp_and_aftale_from_file(data: str) -> dict[str, list]:
    """Given a text file from FPLKA in SAP, this method will create a dictionary with ForretnPartner as key,
    and a list of aftaler as value.
    The file expected to be exported as "regneark" and saved as a text file.

    Args:
        data: A string of all the data in the file.

    Returns: Dictionary of ForretnPartner and aftaler.
    """

    fp = ""
    fp_aftale = {}

    for line in data.split('\n'):

        if line.startswith("\tForretnPartner:"):
            # set active fp "key"
            fp = line.split("\t")[-1]
            fp_aftale[fp] = []
        elif len(line) > 0 and line[1].isdigit():
            fp_aftale[fp].append(line.split("\t")[1].lstrip('0')[:-12])

    return fp_aftale
