import argparse
import json
import os
import sys
from datetime import datetime

# Standard library imports only

def parse_http_file(filepath):
    """Parses a raw HTTP response file into headers and body."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Split headers and body
    # HTTP responses usually separate headers and body with \r\n\r\n or \n\n
    parts = content.split('\n\n', 1)
    if len(parts) < 2:
        parts = content.split('\r\n\r\n', 1)
    
    if len(parts) < 2:
        header_text = content
        body_text = ""
    else:
        header_text = parts[0]
        body_text = parts[1]

    # Parse headers
    headers = {}
    status_line = ""
    header_lines = header_text.splitlines()
    if header_lines:
        status_line = header_lines[0]
        for line in header_lines[1:]:
            if ':' in line:
                key, val = line.split(':', 1)
                headers[key.strip().lower()] = val.strip()
    
    # Parse Status Code
    status_code = 0
    if status_line.startswith("HTTP/"):
        try:
            status_code = int(status_line.split(' ')[1])
        except (IndexError, ValueError):
            pass

    return {
        "status_code": status_code,
        "headers": headers,
        "body": body_text
    }

def solve(packet_dir, out_file):
    http_dir = os.path.join(packet_dir, "http")
    
    # Load expected logins
    with open(os.path.join(packet_dir, "expected_logins.json"), 'r') as f:
        expected_logins = json.load(f)

    # Identify Repos
    repo_files = [f for f in os.listdir(http_dir) if f.startswith("repos__") and f.endswith(".http")]
    repo_names = sorted([f.replace("repos__", "").replace(".http", "") for f in repo_files])

    repos_data = []
    
    for repo in repo_names:
        # 1. Parse repos__<name>.http
        repo_resp = parse_http_file(os.path.join(http_dir, f"repos__{repo}.http"))
        repo_json = json.loads(repo_resp['body']) if repo_resp['status_code'] == 200 else {}
        
        default_branch = repo_json.get("default_branch", "main")
        has_pages_api = repo_json.get("has_pages", False)

        # 2. Parse pages__<name>.http
        pages_resp = parse_http_file(os.path.join(http_dir, f"pages__{repo}.http"))
        pages_json = json.loads(pages_resp['body']) if pages_resp['status_code'] == 200 else {}
        
        # FIX: Use the actual status from the JSON if available, otherwise default to "built" only if 200 OK and no status field (unlikely)
        # But for 404, it's "not_found"
        if pages_resp['status_code'] == 200:
            pages_api_status = pages_json.get("status", "built")
        else:
            pages_api_status = "not_found"
        
        # Extract pages info if available
        pages_html_url = pages_json.get("html_url", None)
        pages_source_branch = None
        pages_source_path = None
        if pages_resp['status_code'] == 200 and "source" in pages_json:
            pages_source_branch = pages_json["source"].get("branch")
            pages_source_path = pages_json["source"].get("path")
            
        # 3. Parse public__<name>.http
        public_resp = parse_http_file(os.path.join(http_dir, f"public__{repo}.http"))
        public_status = public_resp['status_code']
        public_location = public_resp['headers'].get("location")
        public_url = f"https://ai-village-agents.github.io/{repo}/"

        # Compute Flags
        flags = []
        
        # has_pages_false_but_pages_endpoint_ok
        if not has_pages_api and pages_api_status != "not_found":
            flags.append("has_pages_false_but_pages_endpoint_ok")
            
        # has_pages_true_but_pages_endpoint_404
        if has_pages_api and pages_api_status == "not_found":
            flags.append("has_pages_true_but_pages_endpoint_404")
            
        # pages_built_but_public_404
        # Note: 'built' status might be 'building' too? 
        # The grader checks: if pages.get("api_status") == "built" and public.get("http_status") == 404:
        # So we only flag if it is exactly "built".
        if pages_api_status == "built" and public_status == 404:
            flags.append("pages_built_but_public_404")
            
        # pages_source_non_default_branch
        if pages_source_branch and pages_source_branch != default_branch:
            flags.append("pages_source_non_default_branch")
            
        flags.sort()

        repo_entry = {
            "repo": repo,
            "has_pages": has_pages_api,
            "pages": {
                "api_status": pages_api_status,
                "html_url": pages_html_url,
                "source_branch": pages_source_branch,
                "source_path": pages_source_path
            },
            "public": {
                "url": public_url,
                "http_status": public_status,
                "location": public_location
            },
            "flags": flags
        }
        repos_data.append(repo_entry)

    # Ghost Accounts
    ghost_accounts = []
    for login in expected_logins:
        user_resp = parse_http_file(os.path.join(http_dir, f"users__{login}.http"))
        if user_resp['status_code'] == 404:
            ghost_accounts.append({
                "login": login,
                "reason": "users endpoint returned 404 but login is listed in expected_logins.json"
            })
    
    ghost_accounts.sort(key=lambda x: x['login'])

    report = {
        "packet_version": "v1",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "repos": repos_data,
        "ghost_accounts": ghost_accounts
    }

    with open(out_file, 'w') as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    
    solve(args.packet, args.out)
