import os
import json
def parse_request_file(file_path):
    """Parses a single HTTP request file and extracts key information."""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    headers = {}
    for line in lines[1:]:
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip()] = value.strip()
    # Extract the request line (e.g., "GET /path/to/resource HTTP/1.1")
    request_line = lines[0].strip().split()
    method = request_line[0]
    path = request_line[1]
    return {
        'user_agent': headers.get('User-Agent'),
        'method': method,
        'path': path
    }
def generate_report(directory):
    """Generates a JSON report of all parsed request files in a directory."""
    report = {}
    for filename in os.listdir(directory):
        if filename.endswith(".req"):
            file_path = os.path.join(directory, filename)
            report[filename] = parse_request_file(file_path)
    return report
if __name__ == "__main__":
    requests_dir = 'requests' 
    report_data = generate_report(requests_dir)
    with open('report.json', 'w') as f:
        json.dump(report_data, f, indent=4)

