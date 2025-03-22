import sys
import os
from flask import Flask, request, jsonify
import threading
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scanners.zap_scanner import start_scan, check_scan_status, get_scan_results
from flask_cors import CORS
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
active_scans = {}
@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('frontend/images', filename)
@app.route('/start_scan', methods=['POST'])
def start_scan_route():
    """API to start a scan"""
    data = request.json
    target_url = data.get("url")
    if not target_url:
        return jsonify({"error": "URL is required"}), 400
    scan_id = start_scan(target_url)
    if scan_id:
        thread = threading.Thread(target=check_scan_status, args=(scan_id,))
        thread.start()
        active_scans[scan_id] = target_url
        return jsonify({"message": "Scan started", "scan_id": scan_id})
    else:
        return jsonify({"error": "Failed to start scan"}), 500
@app.route('/scan_status/<scan_id>', methods=['GET'])
def scan_status(scan_id):
    """API to check scan progress"""
    if scan_id not in active_scans:
        print(f"❌ Scan ID {scan_id} not found in active scans.")
        return jsonify({"scan_id": scan_id, "status": "0"}), 200 
    status = check_scan_status(scan_id)
    if status is None:
        return jsonify({"scan_id": scan_id, "status": "0"}), 200 
    return jsonify({"scan_id": scan_id, "status": status})
@app.route('/scan_results', methods=['GET'])
def scan_results():
    """API to get scan results"""
    results = get_scan_results()
    formatted_results = {
        "High Risk": [],
        "Medium Risk": [],
        "Low Risk": [],
        "Informational": []
    }
    for item in results:
        risk_level = item["Risk"].lower()
        if "high" in risk_level:
            formatted_results["High Risk"].append(item)
        elif "medium" in risk_level:
            formatted_results["Medium Risk"].append(item)
        elif "low" in risk_level:
            formatted_results["Low Risk"].append(item)
        else:
            formatted_results["Informational"].append(item)
    return jsonify(formatted_results)
from flask import send_from_directory
@app.route("/")
def serve_frontend():
    return send_from_directory("../frontend", "index.html")
@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("../frontend", path)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
