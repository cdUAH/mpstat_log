#!/bin/bash

# cldeitzler
# 6/12/25

# Set constants and paramenters
MAX_SIZE=$((512 * 1024 * 1024)) # 500 mb
MAX_FILES=5 # Amount of files in loop
INTERVAL=5 # Runs every 5 seconds

# Check if a log directory is provided as an argument
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <log_directory> <cores: 0,1,2,n or 0-2>"
    exit 1
fi

LOG_DIR_INIT="$1"
LOG_DIR="$LOG_DIR_INIT/logs" # safety to ensure all logs are in new unique log directory
CORES="$2" # User adds what cores (htop or alternative to see)
mkdir -p "$LOG_DIR"
DIAG_FILE="$LOG_DIR/mpstat_diag.log"


# Function to check log file size and rotate if needed. Fails over to new log file after 1GB
rotate_log() {
    if [ ! -f "$LOG_FILE" ] || [ $(stat -c%s "$LOG_FILE") -ge $MAX_SIZE ]; then
        LOG_FILE="$LOG_DIR/mpstat_log_$(date +%m%d%Y%).log"
        echo "[SCRIPT] [$(date '+%Y-%m-%d %H:%M:%S')] Created new file $LOG_FILE based on max size: $MAX_SIZE MB" >> $DIAG_FILE #echo status to diag_log
    fi
}

cleanup_log(){
    local files=("$LOG_DIR"/*.log) #creates array of files in logdir
    local count=${#files[@]} # counts the length of that array to get number of log files

    if (( count > MAX_FILES )); then
        PRIME_DELETE_FILE=$(ls -1t "$LOG_DIR"/*.log | tail -n +$((MAX_FILES + 1))) # get file for deletion
        echo "[SCRIPT] [$(date '+%Y-%m-%d %H:%M:%S')] Routine DELETE file: $PRIME_DELETE_FILE based on max size: $MAX_SIZE MB and max files: $MAX_FILES" >> $DIAG_FILE #echo status to diag_log
        ls -1t "$LOG_DIR"/*.log | tail -n +$((MAX_FILES + 1)) | xargs rm -f
        echo "[SCRIPT] [$(date '+%Y-%m-%d %H:%M:%S')] Delete completed" >> $DIAG_FILE
    fi
}
# Function to log mpstat output.
# Includes both epoch (date +%s) and actual (date) to allow easy read-in to dataframe for data analysis
# Outputs any errors (probably none) to an dianostic file.
dump_mpstat() {
    rotate_log
    cleanup_log
    mpstat -P $CORES | while read -r line; do
    MEMORY="$(free -m | awk '/Mem:/ {printf "%6d M used, %6d M free", $3, $4}')"
    echo "$(date +%s) $(date +'%d %B %Y %Z') $line" "|" $MEMORY; done >> "$LOG_FILE" 2>> "$DIAG_FILE"
    echo "" >> "$LOG_FILE"
}
loop() {

# Logs until stopped
while true; do
    dump_mpstat
    sleep $INTERVAL
done
}
# Echos location and PID
PID=$!
echo "mpstat logging started in the background. Logs are stored in $LOG_FILE"
echo "Script actions are logged in $DIAG_FILE"
echo "PID: $PID"
loop
