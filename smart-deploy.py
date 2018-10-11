#!/usr/bin/python3
import signal
import sys
import threading
import os

run_lock  = threading.Lock()
targetDir = ""
srcICS    = ""
def wrapper(a,w):
    t = threading.Thread(target=handleUpdateRequest)
    t.start()

def handleUpdateRequest():
    global run_lock

    try:
        run_lock.acquire_lock()
        os.system("./dumb-deploy.sh {} {}".format(srcICS, targetDir))
        print("Rebuilt")
    finally:
        run_lock.release()

if __name__ == "__main__":
    if len(sys.argv) <= 2:
        print("Ussage: ./deploy.sh [ICS-FILE] [DEPLOY-TARGET]")
        sys.exit(1)

    srcICS = sys.argv[1]
    targetDir = sys.argv[2]

    print("src: {}\ntarget: {}".format(srcICS, targetDir))

    signal.signal(signal.SIGUSR1, wrapper)
    while True:
        signal.pause()
