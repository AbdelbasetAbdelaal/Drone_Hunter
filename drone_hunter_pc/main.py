"""
================================================================================
                    DRONE HUNTER 2D - ENTRY POINT
================================================================================
Application launcher for Drone Hunter PC 2D Edition.
Initializes runtime pathing, instantiates the core Game engine, and starts
the primary loop with safe top-level exception logging.
"""

import os
import sys
import logging
import traceback

# Ensure the root package directory is always on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from src.core.game import Game

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    logging.info("Starting Drone Hunter 2D [PC Edition]...")

    try:
        game = Game()
        game.run()
    except Exception as e:
        logging.critical(f"Fatal error during game execution: {e}")
        crash_log_path = os.path.join(CURRENT_DIR, "crash_log_pc.txt")
        with open(crash_log_path, "w", encoding="utf-8") as f:
            f.write(f"Fatal Error: {e}\n\n")
            traceback.print_exc(file=f)
        raise

if __name__ == "__main__":
    main()
