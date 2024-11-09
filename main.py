from flask import Flask, request, jsonify
import requests
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the IDM-VTON API URLs
IDM_VTON_QUEUE_URL = "https://yisol-idm-vton.hf.space/queue/join"
IDM_VTON_QUEUE_DATA_URL = "https://yisol-idm-vton.hf.space/queue/data?session_hash="

@app.route('/forward', methods=['POST'])
def forward_request():
    try:
        # Extract the JSON payload from the incoming request
        payload = request.json
        if not payload:
            return jsonify({"error": "No JSON payload found in request"}), 400

        
        # Forward the request to IDM-VTON's queue/join endpoint
        headers = {"Content-Type": "application/json"}
        logger.info("Forwarding payload to IDM-VTON queue join endpoint")
        
        response = requests.post(IDM_VTON_QUEUE_URL, json=payload, headers=headers)

        # If the request to IDM-VTON fails
        if response.status_code != 200:
            logger.error(f"Failed to contact IDM-VTON: {response.text}")
            return jsonify({"error": "Failed to contact IDM-VTON", "details": response.text}), response.status_code

        # Return the response from IDM-VTON
        return jsonify(response.json()), response.status_code

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_data', methods=['GET'])
def get_queue_data():
    try:
        # Get the session hash from the query parameters
        session_hash = request.args.get('session_hash')

        if not session_hash:
            return jsonify({"error": "No session hash provided"}), 400

        # Construct the queue data URL
        queue_data_url = IDM_VTON_QUEUE_DATA_URL + session_hash
        
        # Poll for the result from IDM-VTON
        logger.info(f"Polling queue data for session hash: {session_hash}")
        response = requests.get(queue_data_url)

        print("response :- ", response.text)
        # If the request to IDM-VTON fails
        if response.status_code != 200:
            logger.error(f"Failed to poll IDM-VTON queue data: {response.text}")
            return jsonify({"error": "Failed to poll IDM-VTON queue data", "details": response.text}), response.status_code

        # Return the response from IDM-VTON queue data
        return response.text, response.status_code

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500
