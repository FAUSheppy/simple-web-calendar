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
    menubar.innerText = "Heute"

    var elem = doc.getElementById("menubarDate");
    elem.parentNode.removeChild(elem);

    /* put it together */
    document.body.innerHTML += doc.body.innerHTML
}

function runShit(){
    
    /* install service worker */
    //if ('serviceWorker' in navigator && location.protocol != "file:") {
    //    navigator.serviceWorker.register('js/worker.js')
    //}
    
    /* input time */
    element = document.getElementById("time")
    strftime = {weekday: 'long', month: 'long', day: 'numeric', year: 'numeric', hour: "2-digit", minute: "2-digit", timeZoneName: "short"};
    time = new Intl.DateTimeFormat("de",strftime).format()
    if(element){
        element.textContent = time
    }
    
    /* highlight current day */
    var date = new Date()
    month = date.getMonth() + 1
    if(month < 10){
        monthStr = "0" + month.toString()
    }
    if(window.location.href.includes("&" + monthStr)){
        element = document.getElementById("day-"+date.getDate())
        if(element){
          element.style.background = "orange"
        }
    }

    /* upcoming */
    if(window.location.href.includes("month-")){
      link = "/day-" + date.getFullYear()   + "&" + 
                       monthStr             + "&" + 
                       date.getDate()       + ".html"
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

function detectswipe(el,func) {
  swipe_det = new Object();

  swipe_det.sX = 0; 
	swipe_det.sY = 0;
  swipe_det.eX = 0;
	swipe_det.eY = 0;

  var min_x = 250;  //min x swipe for horizontal swipe
  var max_y = 10;  //max y difference for horizontal swipe

  var direc = "";
  el.addEventListener('touchstart', function(e){
    var t = e.touches[0];
    swipe_det.sX = t.screenX; 
    swipe_det.sY = t.screenY;
  }, false);
  el.addEventListener('touchmove', function(e){
    e.preventDefault();
    var t = e.touches[0];
    swipe_det.eX = t.screenX; 
    swipe_det.eY = t.screenY;    
  }, false);
  el.addEventListener('touchend',function(e){
    if (( swipe_det.eX - min_x > swipe_det.sX || swipe_det.eX + min_x < swipe_det.sX ) && 
				( swipe_det.eY < swipe_det.sY + max_y && swipe_det.sY > swipe_det.eY - max_y   && 
					swipe_det.eX > 0)){
      if(swipe_det.eX > swipe_det.sX){
				direc = "r";
			}else{
				 direc = "l";
			}
    }

    if (direc != "") {
    	func(el, direc);
    }

    direc = "";
  }, false);  
}

function myfunction(el, d) {
	if(!window.location.includes("day-")){
		return
	}
	if(d == "r"){
		alert("lol")
	}
}

detectswipe(document.body,myfunction);
window.addEventListener('online', goOnline);
window.addEventListener('offline', goOffline);
window.onload = runShit
