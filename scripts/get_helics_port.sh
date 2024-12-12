#!/bin/bash

# Function to check if a port is in use
is_port_in_use() {
    local port=$1
    # Use netstat to check if the port is already listening
    netstat -tuln | grep -q ":$port "
}

# Find 10 consecutive empty ports
find_consecutive_empty_ports() {
    local start_port=${1:-10000}  # Default start port if not specified
    local max_port=${2:-65535}   # Maximum port to check
    local consecutive_count=10   # Number of consecutive empty ports to find

    for ((port=start_port; port<=max_port; port++)); do
        # Check if next 10 ports are free
        local is_consecutive_free=true
        for ((check=port; check<port+consecutive_count; check++)); do
            if is_port_in_use $check; then
                is_consecutive_free=false
                break
            fi
        done

        # If consecutive ports are free, export the first port and return
        if [ "$is_consecutive_free" = true ]; then
            export HELICS_PORT=$port
            echo "Found 10 consecutive empty ports starting at $port"
            echo "Exported HELICS_PORT=$port"
            return 0
        fi
    done

    # If no consecutive free ports found
    echo "No $consecutive_count consecutive empty ports found between $start_port and $max_port" >&2
    return 1
}

# Main script
# Allow optional start port as first argument
if [ $# -eq 0 ]; then
    find_consecutive_empty_ports
elif [ $# -eq 1 ]; then
    find_consecutive_empty_ports $1
elif [ $# -eq 2 ]; then
    find_consecutive_empty_ports $1 $2
else
    echo "Usage: $0 [start_port] [max_port]"
    exit 1
fi
