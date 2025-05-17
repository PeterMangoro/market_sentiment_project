import os
import sys

# Add the parent directory of this script to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_keys import MARKETAUX_API_KEY

print(MARKETAUX_API_KEY)
