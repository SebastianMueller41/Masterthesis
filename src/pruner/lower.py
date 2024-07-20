from src.tree.basepruner import BasePruner
import logging
from src.structs.logger import setup_logging


# Set up logging for this module
setup_logging()

# Get the logger for this module
tree_logger = logging.getLogger(__name__)

class LowerPruner(BasePruner):
    def __init__(self, tree, brancher):
        self.tree = tree
        self.brancher = brancher