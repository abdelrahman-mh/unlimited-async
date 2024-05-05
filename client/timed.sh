#!/bin/bash

# Run the Python application with time command
/usr/bin/time --format "Memory usage: %MKB\tTime: %e seconds\tCPU usage: %P" "$@"
