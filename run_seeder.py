"""
Run the database seeder
"""

import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Brick_Backend.seed_data import main

if __name__ == "__main__":
    print("\n🚀 Starting Brick Backend Seeder...\n")
    main()