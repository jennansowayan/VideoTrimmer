
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask

app = Flask(__name__)

# Configure logging
if not app.debug:
    # Log errors to a file
    file_handler = RotatingFileHandler('error.log', maxBytes=10000, backupCount=1)
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    app.logger.addHandler(file_handler)

app.secret_key = 'your_secret_key'

# Your routes and other configuration here

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000,debug=True)
