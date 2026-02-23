#!/usr/bin/env bash

set -euo pipefail

ORG="ai-village-agents"

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Required command '$cmd' not found. Please install it first." >&2
    exit 1
  fi
}

fetch_json() {
  local url="$1"
  if ! data=$(curl -fsSL "$url" 2>/dev/null); then
    echo ""
    return 1
  fi
  printf "%s" "$data"
  return 0
}

event_count_section() {
  echo "### Event Count"
  echo ""
  local log_url="https://raw.githubusercontent.com/ai-village-agents/village-event-log/main/events.json"
  local chronicle_url="https://raw.githubusercontent.com/ai-village-agents/village-chronicle/main/docs/events.json"
  local dashboard_url="https://ai-village-agents.github.io/repo-health-dashboard/"

  local log_count="n/a" chronicle_count="n/a" dashboard_count="n/a"
  local log_status="missing" chronicle_status="missing" dashboard_status="unreachable"

  if log_data=$(fetch_json "$log_url") && log_count=$(printf "%s" "$log_data" | jq -r '.metadata.total_events // empty' 2>/dev/null) && [[ -n "$log_count" ]]; then
    log_status="ok"
  else
    log_count="n/a"
    log_status="invalid or missing"
  fi

  if chronicle_data=$(fetch_json "$chronicle_url") && chronicle_count=$(printf "%s" "$chronicle_data" | jq -r '.events | length' 2>/dev/null); then
    chronicle_status="ok"
  else
    chronicle_count="n/a"
    chronicle_status="invalid or missing"
  fi

  if dashboard_html=$(curl -fsSL "$dashboard_url" 2>/dev/null); then
    if dashboard_count=$(printf "%s" "$dashboard_html" | grep -Eo 'Total Events[^0-9]*[0-9]+' | head -n1 | grep -Eo '[0-9]+'); then
      dashboard_status="ok"
    else
      dashboard_status="not found in page"
      dashboard_count="n/a"
    fi
  else
    dashboard_status="unreachable"
    dashboard_count="n/a"
  fi

  echo "| Source | Count | Status |"
  echo "| --- | --- | --- |"
  echo "| village-event-log (.metadata.total_events) | ${log_count} | ${log_status} |"
  echo "| village-chronicle (/docs/events.json length) | ${chronicle_count} | ${chronicle_status} |"
  echo "| repo-health-dashboard (scraped) | ${dashboard_count} | ${dashboard_status} |"
  echo ""

  local alignment_status="Needs manual check"
  if [[ "$log_count" =~ ^[0-9]+$ && "$chronicle_count" =~ ^[0-9]+$ ]]; then
    if [[ "$log_count" == "$chronicle_count" ]]; then
      alignment_status="PASS"
    else
      alignment_status="FAIL"
    fi
  fi

  echo "- Alignment (event-log vs chronicle): **${alignment_status}**"

  if [[ "$dashboard_count" =~ ^[0-9]+$ && "$log_count" =~ ^[0-9]+$ ]]; then
    local dashboard_alignment
    if [[ "$dashboard_count" == "$log_count" ]]; then
      dashboard_alignment="PASS"
    else
      dashboard_alignment="FAIL"
    fi
    echo "- Alignment (event-log vs repo-health-dashboard): **${dashboard_alignment}**"
  else
    echo "- Alignment (repo-health-dashboard): **Not available**"
  fi
  echo ""
}

pages_status_section() {
  echo "### Pages Status"
  echo ""
  local repos
  repos=$(gh api "/orgs/${ORG}/repos?per_page=100")
  local total_repos=0 pages_enabled=0 serving_200=0
  local broken_repos=() table_lines=()

  while IFS=$'\t' read -r name has_pages; do
    ((total_repos++))
    local enabled url http_code
    if [[ "$has_pages" == "true" ]]; then
      ((pages_enabled++))
      enabled="yes"
      url=$(gh api "/repos/${ORG}/${name}/pages" --jq '.html_url' 2>/dev/null || echo "https://${ORG}.github.io/${name}/")
      http_code=$(curl -o /dev/null -s -w "%{http_code}" "$url" || echo "error")
      if [[ "$http_code" == "200" ]]; then
        ((serving_200++))
      else
        broken_repos+=("${name} (${http_code})")
      fi
    else
      enabled="no"
      url="-"
      http_code="-"
    fi
    table_lines+=("| ${name} | ${enabled} | ${url} | ${http_code} |")
  done <<< "$(printf "%s" "$repos" | jq -r '.[] | "\(.name)\t\(.has_pages)"')" || true

  echo "- Total Repos: ${total_repos}"
  echo "- Pages Enabled: ${pages_enabled}"
  echo "- Serving 200: ${serving_200}"
  echo "- Broken: ${#broken_repos[@]}"
  echo ""

  if [[ "${#broken_repos[@]}" -gt 0 ]]; then
    echo "Broken repos:"
    for broken in "${broken_repos[@]}"; do
      echo "- ${broken}"
    done
    echo ""
  fi

  echo "| Repo | Pages Enabled | URL | HTTP |"
  echo "| --- | --- | --- | --- |"
  for line in "${table_lines[@]}"; do
    echo "$line"
  done
  echo ""
}

timestamp_section() {
  echo "### Latest Commit Timestamps"
  echo ""
  local repos=(
    "village-event-log"
    "village-chronicle"
    "village-directory"
    "repo-health-dashboard"
    "village-challenges"
  )
  echo "| Repo | Commit SHA | Timestamp | Author |"
  echo "| --- | --- | --- | --- |"
  for repo in "${repos[@]}"; do
    local commit sha date author
    commit=$(gh api "/repos/${ORG}/${repo}/commits?per_page=1" | jq '.[0]')
    sha=$(printf "%s" "$commit" | jq -r '.sha // "n/a"')
    date=$(printf "%s" "$commit" | jq -r '.commit.author.date // "n/a"')
    author=$(printf "%s" "$commit" | jq -r '.commit.author.name // "n/a"')
    echo "| ${repo} | ${sha} | ${date} | ${author} |"
  done
  echo ""
}

ci_status_section() {
  echo "### Latest CI Workflow Runs"
  echo ""
  local repos=(
    "village-event-log"
    "village-chronicle"
    "repo-health-dashboard"
    "open-ics"
    "village-collab-graph"
  )
  echo "| Repo | Status | Conclusion | Updated |"
  echo "| --- | --- | --- | --- |"
  for repo in "${repos[@]}"; do
    local run status conclusion updated
    run=$(gh api "/repos/${ORG}/${repo}/actions/runs?per_page=1" | jq '.workflow_runs[0]')
    status=$(printf "%s" "$run" | jq -r '.status // "n/a"')
    conclusion=$(printf "%s" "$run" | jq -r '.conclusion // "n/a"')
    updated=$(printf "%s" "$run" | jq -r '.updated_at // "n/a"')
    echo "| ${repo} | ${status} | ${conclusion} | ${updated} |"
  done
  echo ""
}

metadata_section() {
  echo "### Metadata Consistency"
  echo ""
  local event_log_url="https://raw.githubusercontent.com/ai-village-agents/village-event-log/main/events.json"
  local chronicle_readme_url="https://raw.githubusercontent.com/ai-village-agents/village-chronicle/main/README.md"
  local chronicle_events_url="https://raw.githubusercontent.com/ai-village-agents/village-chronicle/main/docs/events.json"

  local event_data chronicle_events_data chronicle_readme
  if ! event_data=$(fetch_json "$event_log_url"); then
    event_data=""
  fi
  if ! chronicle_events_data=$(fetch_json "$chronicle_events_url"); then
    chronicle_events_data=""
  fi
  chronicle_readme=$(curl -fsSL "$chronicle_readme_url" 2>/dev/null || echo "")

  local event_last_updated="n/a" event_version="n/a"
  local chronicle_last_updated="n/a" chronicle_version="n/a"

  if [[ -n "$event_data" ]]; then
    event_last_updated=$(printf "%s" "$event_data" | jq -r '.metadata.last_updated // empty' 2>/dev/null || true)
    event_version=$(printf "%s" "$event_data" | jq -r '.metadata.version // empty' 2>/dev/null || true)
    [[ -z "$event_last_updated" ]] && event_last_updated="n/a"
    [[ -z "$event_version" ]] && event_version="n/a"
  fi

  if [[ -n "$chronicle_events_data" ]]; then
    chronicle_last_updated=$(printf "%s" "$chronicle_events_data" | jq -r '.metadata.last_updated // empty' 2>/dev/null || true)
    chronicle_version=$(printf "%s" "$chronicle_events_data" | jq -r '.metadata.version // empty' 2>/dev/null || true)
    [[ -z "$chronicle_last_updated" ]] && chronicle_last_updated="n/a"
    [[ -z "$chronicle_version" ]] && chronicle_version="n/a"
  fi

  if [[ "$chronicle_last_updated" == "n/a" && -n "$chronicle_readme" ]]; then
    chronicle_last_updated=$( { printf "%s" "$chronicle_readme" | grep -i -m1 'last[_ ]updated' || true; } | sed -E 's/.*last[_ ]updated[^0-9A-Za-z]*//I' | xargs)
    [[ -z "$chronicle_last_updated" ]] && chronicle_last_updated="n/a"
  fi

  if [[ "$chronicle_version" == "n/a" && -n "$chronicle_readme" ]]; then
    chronicle_version=$( { printf "%s" "$chronicle_readme" | grep -i -m1 '^version' || true; } | sed -E 's/^[Vv]ersion[: ]*//' | xargs)
    [[ -z "$chronicle_version" ]] && chronicle_version="n/a"
  fi

  echo "| Field | village-event-log | village-chronicle |"
  echo "| --- | --- | --- |"
  echo "| last_updated | ${event_last_updated} | ${chronicle_last_updated} |"
  echo "| version | ${event_version} | ${chronicle_version} |"
  echo ""

  if [[ "$event_last_updated" != "n/a" && "$chronicle_last_updated" != "n/a" ]]; then
    if [[ "$event_last_updated" == "$chronicle_last_updated" ]]; then
      echo "- last_updated alignment: **PASS**"
    else
      echo "- last_updated alignment: **FAIL** (${event_last_updated} vs ${chronicle_last_updated})"
    fi
  else
    echo "- last_updated alignment: **Not available**"
  fi

  if [[ "$event_version" != "n/a" && "$chronicle_version" != "n/a" ]]; then
    if [[ "$event_version" == "$chronicle_version" ]]; then
      echo "- version alignment: **PASS**"
    else
      echo "- version alignment: **FAIL** (${event_version} vs ${chronicle_version})"
    fi
  else
    echo "- version alignment: **Not available**"
  fi
  echo ""
}

main() {
  require_cmd gh
  require_cmd jq
  require_cmd curl

  echo "# AI Village Infrastructure Audit"
  echo ""
  echo "_Generated on $(date -u +"%Y-%m-%d %H:%M:%S UTC")_"
  echo ""

  event_count_section
  pages_status_section
  timestamp_section
  ci_status_section
  metadata_section
}

main "$@"
