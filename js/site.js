if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('service-worker.js')
}

/* highlight current day */
var els = document.querySelectorAll("a[href='http://domain.com']");

/* input time */
element = document.getElementById("time")
strftime = {weekday: 'long', month: 'long', day: 'numeric', year: 'numeric', hour: "2-digit", minute: "2-digit", timeZoneName: "short"};
time = new Intl.DateTimeFormat("de",strftime).format()
element.textContent = time

/* highlight current day */
var date = new Date()
element = document.getElementById("day-"+date.getDate())
element.style.background = "orange"
