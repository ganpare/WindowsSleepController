# Alexa Sleep Controller for Windows

A Python-based Windows service that allows Amazon Alexa to remotely trigger sleep mode via AWS.

## Features

- **Remote Sleep Control**: Put your Windows PC to sleep using voice commands via Alexa
- **Secure API**: Protected API endpoint with key authentication
- **Windows Service**: Runs in the background as a Windows service
- **Web Control Panel**: Simple dashboard to manage API keys and monitor sleep requests
- **Logging**: Detailed logs for troubleshooting

## Installation

### Prerequisites

- Windows 10 or newer
- Python 3.6 or newer
- Administrator privileges (for service installation)

### Setup Instructions

1. **Download the package** and extract it to a location of your choice.

2. **Run the installer**:
   - Double-click `install_service.bat` to install and start the service.
   - This script will install required Python packages and set up the Windows service.

3. **Access the control panel**:
   - Open a web browser and navigate to: `http://localhost:5000`
   - Default login credentials:
     - Username: `admin`
     - Password: `admin`
   - **Important**: Change these credentials for security!

4. **Generate an API key**:
   - In the control panel, click "Generate New Key"
   - Save this key securely - it will only be shown once

## Setting Up Alexa Integration

### Method 1: Automated AWS Lambda Integration (Recommended)

This application now features an automated AWS Lambda function generator that creates and configures everything for you:

1. **Generate API Key with AWS Lambda Integration**:
   - In the control panel, click "Generate New Key" and select "Generate API Key with AWS Lambda Integration"
   - Enter your AWS credentials and desired configuration
   - The system will automatically create a Lambda function configured to work with your endpoint

2. **Set Up Alexa Skill**:
   - Follow the instructions provided on the success page
   - Copy the generated JSON for your Alexa Skill
   - Set up the skill using the Alexa Developer Console and the provided Lambda ARN

### Method 2: Manual Setup

If you prefer to set up AWS Lambda manually:

1. **Create an AWS Lambda function**:
   - Go to AWS Lambda and create a new function
   - Use a Node.js or Python runtime
   - Implement code that sends a POST request to your endpoint with the API key

2. **Create an Alexa Skill**:
   - In the Alexa Developer Console, create a custom skill
   - Configure intents for triggering sleep mode
   - Link the skill to your Lambda function

### Network Configuration

To access your PC from outside your home network:

- Set up port forwarding on your router (forward port 5000 to your PC's local IP)
- Alternatively, use a service like ngrok for secure tunneling

For detailed Windows setup instructions, see [WINDOWS_SETUP.md](WINDOWS_SETUP.md).

## Sample Lambda Function (Node.js)

```javascript
const axios = require('axios');

exports.handler = async function(event, context) {
    try {
        const response = await axios.post('http://your-endpoint:5000/api/sleep', {}, {
            headers: {
                'X-API-Key': 'your-api-key'
            }
        });
        
        return {
            statusCode: 200,
            body: JSON.stringify('I\'ll put your computer to sleep now.')
        };
    } catch (error) {
        console.error('Error:', error);
        return {
            statusCode: 500,
            body: JSON.stringify('Sorry, I couldn\'t put your computer to sleep.')
        };
    }
};
