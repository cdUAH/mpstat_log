#!/bin/bash

# Cooper Deitzler cooper.l.deitzler@nasa.gov
# 3/3/25

# Check if a log directory is provided as an argument
if [ -z "$1" ]; then
    echo "Usage: $0 <log_directory> (MUST BE ROOT)"
    exit 1
fi

LOG_DIR="$1"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/mpstat_log_$(date +%m%d%Y).log"
ERR_FILE="$LOG_DIR/mpstat_err.log"
CORES="3,18,19" # Runs cores 4, 19, 20 (primary)

MAX_SIZE=$((1024 * 1024 * 1024)) # 1GB in bytes
INTERVAL=5  # Runs every 5 seconds

# Function to check log file size and rotate if needed. Fails over to new log file after 1GB
rotate_log() {
    if [ -f "$LOG_FILE" ] && [ $(stat -c%s "$LOG_FILE") -ge $MAX_SIZE ]; then
        LOG_FILE="$LOG_DIR/mpstat_log_$(date +%m%d%Y).log"
    fi
}

# Function to log mpstat output.
# Includes both epoch (date +%s) and actual (date) to allow easy read-in to dataframe for data analysis
# Outputs any errors (probably none) to an error file. 
dump_mpstat() {
    rotate_log
    mpstat -P $CORES $INTERVAL | while read -r line; do echo "$(date +%s) ($(date)) $line"; done >> "$LOG_FILE" 2>>"$ERR_FILE"
    echo "" >> "$LOG_FILE"
}

# Logs until stopped
while true; do
    dump_mpstat
done &

# Echos location and PID
PID=$!
echo "mpstat logging started in the background. Logs are stored in $LOG_FILE"
echo "Errors are logged in $ERR_FILE"
echo "PID: $PID"