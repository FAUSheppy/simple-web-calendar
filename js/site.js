/* install service worker */
if ('serviceWorker' in navigator && location.protocol != "file:") {
    navigator.serviceWorker.register('service-worker.js')
}


/* input time */
element = document.getElementById("time")
strftime = {weekday: 'long', month: 'long', day: 'numeric', year: 'numeric', hour: "2-digit", minute: "2-digit", timeZoneName: "short"};
time = new Intl.DateTimeFormat("de",strftime).format()
if(element){
    element.textContent = time
}

/* highlight current day */
var date = new Date()
if(window.location.href.includes("&"+(date.getMonth()+1).toString())){
    element = document.getElementById("day-"+date.getDate())
    if(element){
    
      element.style.background = "orange"
    }
}
