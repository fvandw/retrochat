#!/bin/bash
# 
# This file is part of the RetroChat distribution (https://github.com/fvandw/retrochat).
# Copyright (c) 2025 fvandw.
# 
# This program is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

cleanup() {
    echo ""
    echo "Disconnecting..."
    if [ -n "$SOCAT_PID" ]; then
        kill $SOCAT_PID 2>/dev/null
        wait $SOCAT_PID 2>/dev/null
    fi
    echo "Done."
    exit
}

trap cleanup SIGINT EXIT

echo "Virtual connection setup..."

socat -d -d pty,raw,echo=0,link=/tmp/client_pty pty,raw,echo=0,link=/tmp/proxy_pty &

SOCAT_PID=$!

echo "------------------------------------------------"
echo "Active process (PID: $SOCAT_PID)"
echo "Client: /tmp/client_pty"
echo "Proxy:  /tmp/proxy_pty"
echo "------------------------------------------------"
echo "Press [ENTER] to quit."

read