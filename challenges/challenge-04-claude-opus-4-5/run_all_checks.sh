#!/bin/bash
#
# Challenge #4: Infrastructure Consistency Audit - MASTER RUNNER
# Runs all audit scripts in sequence for maximum points.
# Total: 100 pts across 5 sections

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_FILE="$SCRIPT_DIR/audit_results_$(date +%Y%m%d_%H%M%S).txt"

echo "============================================================" | tee "$OUTPUT_FILE"
echo "CHALLENGE #4 - INFRASTRUCTURE CONSISTENCY AUDIT" | tee -a "$OUTPUT_FILE"
echo "MASTER AUDIT RUN - $(date -u +%Y-%m-%dT%H:%M:%SZ) UTC" | tee -a "$OUTPUT_FILE"
echo "============================================================" | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

START_TIME=$(date +%s)

# Section 1: Event Count Sync (30 pts)
echo ">>> SECTION 1: Event Count Sync (30 pts) <<<" | tee -a "$OUTPUT_FILE"
python3 "$SCRIPT_DIR/event_count_checker.py" 2>&1 | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

# Section 2: GitHub Pages Status (25 pts)
echo ">>> SECTION 2: GitHub Pages Status (25 pts) <<<" | tee -a "$OUTPUT_FILE"
"$SCRIPT_DIR/pages_status_checker.sh" 2>&1 | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

# Section 3: Timestamp Audit (20 pts)
echo ">>> SECTION 3: Timestamp Audit (20 pts) <<<" | tee -a "$OUTPUT_FILE"
"$SCRIPT_DIR/timestamp_checker.sh" 2>&1 | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

# Section 4: CI/CD Workflow Status (15 pts)
echo ">>> SECTION 4: CI/CD Workflow Status (15 pts) <<<" | tee -a "$OUTPUT_FILE"
"$SCRIPT_DIR/workflow_status_checker.sh" 2>&1 | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "============================================================" | tee -a "$OUTPUT_FILE"
echo "AUDIT COMPLETE" | tee -a "$OUTPUT_FILE"
echo "Duration: ${DURATION} seconds" | tee -a "$OUTPUT_FILE"
echo "Results saved to: $OUTPUT_FILE" | tee -a "$OUTPUT_FILE"
echo "============================================================" | tee -a "$OUTPUT_FILE"

echo ""
echo "📝 Note: Section 5 (Metadata Consistency, 10 pts) requires"
echo "   manual review of discrepancies found in Sections 1-4."
