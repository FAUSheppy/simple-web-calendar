# Introduction
This script can create static web-pages from any ICS-calendar file. It's original purpose was to be used as a read only calendar on mobile devices in conjunction with the [radicale calendar backend](https://radicale.org/). It can be used with any backend which supports a postscript or sending a *SIGUSR1* signal. If everything else fails, you can also use it with *inotifywatch* or *cron*, however this is not recommended.

# Usage
## Dumb deploy
The dumb-deploy scripts simply takes an ICS-file and a target location as arguments, generates the calendar at thus target location and changes the ownership to www-data. This script is useful for testing or usage with *cron* , however it is obviously quite inefficient and, well, dumb. It should generally not be used as a post-script for radicale, as those scripts are run synchronously by default.

    ./dumb-deploy /path/to/ics/file /path/to/target/dir/

## Smart deploy
The smart-deploy script, is called in the same fashion. However, after the first deploy, it will passively wait for a ***SIGURS1*** signal, and only regenerate the calendar once such a signal is received. The systemd template can and should be used for production deployment.

Once the smart deploy script is running in one way or another, you can add the following line in ``[storage]``:

    hook = killall -s USR1 smart-deploy.py

This will send the script the relevant signal and cause it to rebuild the calendar. Note that this option only exists for radicale version >2.0.

# Known problems
* site is poorly sized on bigger screens, meaning mostly desktop computers in general
* pages are not replaced atomically, meaning *404 Errors* are sometimes possible
* the service worker is not working properly

# Future Features planned
* client side javascript to modify calendar entries

# Pictures
## Month View/Main View
![month view](https://media.atlantishq.de/month-view.png)

## Single-Day View
![day view](https://media.atlantishq.de/day-view.png)

## Single-Event/Detailed View
![single event view](https://media.atlantishq.de/event-view.png)


