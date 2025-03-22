import requests
import time
import threading

ZAP_BASE_URL = "http://127.0.0.1:8080"
API_KEY = "a48ki7gnu6od7socnrcv57l69" 

def start_scan(target_url):


    sites_url = f"{ZAP_BASE_URL}/JSON/core/view/sites/?apikey={API_KEY}"
    existing_sites = requests.get(sites_url).json().get("sites", [])

    if target_url in existing_sites:
        print(f"🔍 Target already in scan tree: {target_url} (Skipping spider)")
    else:

        print(f"🕷️ Crawling: {target_url}")
        spider_url = f"{ZAP_BASE_URL}/JSON/spider/action/scan/"
        spider_params = {
            "apikey": API_KEY,
            "url": target_url,
            "maxChildren": 10, 
            "recurse": "false", 
            "subtreeOnly": "true"
        }

        spider_response = requests.post(spider_url, data=spider_params)
        spider_id = spider_response.json().get("scan")

        if not spider_id:
            print(f"❌ Spider error: {spider_response.text}")
            return None

        while True:
            status_url = f"{ZAP_BASE_URL}/JSON/spider/view/status/?apikey={API_KEY}&scanId={spider_id}"
            status = requests.get(status_url).json().get("status")

            if status == "100":
                print("✅ Spider Completed!")
                break
            print(f"🔍 Spider Progress: {status}%")
            time.sleep(2)  


    print(f"🚀 Starting Active Scan on: {target_url}")
    scan_url = f"{ZAP_BASE_URL}/JSON/ascan/action/scan/"
    scan_params = {
        "apikey": API_KEY,
        "url": target_url,
        "recurse": "false", 
        "inScopeOnly": "false",
        "scanPolicyName": "Default Policy",
        "method": "GET", 
        "postData": ""  
    }

    scan_response = requests.post(scan_url, data=scan_params)

    if scan_response.status_code != 200:
        print(f"❌ Scan failed: {scan_response.text}")
        return None

    scan_id = scan_response.json().get("scan")
    print(f"✅ Scan Started: ID {scan_id}")

    return scan_id


def check_scan_status(scan_id):
    """Check and return scan progress in ZAP."""
    status_url = f"{ZAP_BASE_URL}/JSON/ascan/view/status/?apikey={API_KEY}&scanId={scan_id}"
    response = requests.get(status_url)

    if response.status_code != 200:
        print(f"❌ Failed to fetch scan status for scan {scan_id}")
        return "0"

    try:
        progress = response.json().get("status", "0")  
        print(f"✅ Scan {scan_id} Progress: {progress}%")
        return progress
    except Exception as e:
        print(f"❌ JSON Parsing Error: {e}")
        return "0"

def get_scan_results():

    results_url = f"{ZAP_BASE_URL}/JSON/core/view/alerts/?apikey={API_KEY}"
    response = requests.get(results_url)

    results = response.json().get("alerts", [])
    structured_results = [
        {
            "Name": alert["name"],
            "Risk": alert["risk"],
            "Description": alert["description"],
            "Solution": alert.get("solution", "No solution available"),
            "URL": alert["url"]
        }
        for alert in results
    ]

    return structured_results


def async_scan(target_url):
  
    thread = threading.Thread(target=start_scan, args=(target_url,))
    thread.start()


if __name__ == "__main__":
    target = input("🌍 Enter target URL: ")

    print("\n🚀 Running Optimized Scan...")
    scan_id = start_scan(target)

    if scan_id:
        check_scan_status(scan_id)
        results = get_scan_results()

        print("\n📜 Scan Results:")
        print(results)