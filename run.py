import os
import sys

# Set environment variable
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

# Set Python path to include the current directory
sys.path.insert(0, os.path.dirname(__file__))

# Now import and run your app
from app import app

if __name__ == '__main__':
    app.run(debug=True)
