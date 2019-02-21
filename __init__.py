import logging
from . import version
import glob
from os.path import dirname, basename, isfile
# from .modules import *
# from .tasks import *

__log__ = logging.getLogger(__name__)
modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
version.__version__ = "0.1"