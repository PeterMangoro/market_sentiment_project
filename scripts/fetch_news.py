import os
import sys

# Add the parent directory of this script to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_keys import API_TOKEN

print(API_TOKEN)
