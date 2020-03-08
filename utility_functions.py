from datetime import datetime
import math


def ms_til_next_second():
    """
    Return number of milliseconds (expressed as seconds) until next second.
    """

    delay = math.trunc((1000000 - datetime.utcnow().microsecond) / 1000)

    return delay / 1000
