from app import app
import logging

# Configure logging if not already configured
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

# This will be imported by gunicorn in the Replit environment
# But still allow for running with python main.py for local development
if __name__ == "__main__":
    logging.info("Starting Alexa Sleep Service on port 5000")
    app.run(host="0.0.0.0", port=5000)
