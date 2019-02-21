name = "Kiosco 🛍"
version = 0.1
creator = "ferferga"
##This variable is needed by Python for knowing where is the parent package
import sys
import logging
from . import Kiosco
#sys.path.append('/path/to/ptdraft/')

__log__ = logging.getLogger(__name__)
def main():
    Kiosco.load()
if __name__ == "__main__":
    pass
    