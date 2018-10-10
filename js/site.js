
var runOnce = true
function append(){
    /* create pseudo doc for selection */
    var doc = new DOMParser().parseFromString(this.responseText,"text/html")

    /* cause reasons */
    if(!doc.body.innerHTML){
        return
    }
    else if(runOnce){
        runOnce = false
    }else{
        return
    }

    links = doc.getElementsByTagName("a")
    for(i=1; i<links.length; i++){
        links[i].style.textDecoration = "underline"                                                 
    }


    var menubar = doc.getElementsByClassName("menubar")[0]
    menubar.innerText = "Today"

    /* put it together */
    document.body.innerHTML += doc.body.innerHTML
}

function runShit(){
    
    /* install service worker */
    if ('serviceWorker' in navigator && location.protocol != "file:") {
        navigator.serviceWorker.register('js/worker.js')
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

    /* upcoming */
    if(window.location.href.includes("month-")){
      link = "/day-" + date.getFullYear() + "&" + 
                      (date.getMonth()+1) + "&" + 
                       date.getDate() + ".html"
      var xhttp = new XMLHttpRequest();
      xhttp.onreadystatechange = append;
      xhttp.open("GET", link, true);
      xhttp.send();
    }
}

function goOffline(event) {
    el = document.getElementById("offlineInfo")
    el.style.display="block"
}
function goOnline(event) {
    el = document.getElementById("offlineInfo")
    el.style.display="none"
}

window.addEventListener('online', goOnline);
window.addEventListener('offline', goOffline);
window.onload = runShit
