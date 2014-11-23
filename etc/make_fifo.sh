#!/bin/bash

FIFO_FILE="camera.fifo"

# Make FIFO buffer
rm -f "${FIFO_FILE}"
mkfifo "${FIFO_FILE}"
