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

    var menubar = doc.getElementsByClassName("menubar")[0]
    menubar.innerText = "Heute"

    var elem = doc.getElementById("menubarDate");
    elem.parentNode.removeChild(elem);

    /* put it together */
    document.body.innerHTML += doc.body.innerHTML
}

function setCurrentDate(){
    /* input time */
    element = document.getElementById("time")
    strftime = {weekday: 'long', month: 'long', day: 'numeric', year: 'numeric', hour: "2-digit", minute: "2-digit", timeZoneName: "short"};
    time = new Intl.DateTimeFormat("de",strftime).format()
    if(element){
        element.textContent = time
    }
}

function highlightCurrentDay(){

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

}

functionLoadUpcomingEvents(){

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

function addSwipeListeners() {
    swipe_det = new Object();

    swipe_det.sX = 0;
    swipe_det.sY = 0;
    swipe_det.eX = 0;
    swipe_det.eY = 0;

    var min_x = 250;  //min x swipe-length for horizontal swipe
    var max_y = 5;   //max y difference   for horizontal swipe

    var direction = "";

    /* touch start listener */
    window.addEventListener('touchstart', function(e){
        var t = e.touches[0];
        swipe_det.sX = t.screenX;
        swipe_det.sY = t.screenY;
    }, false);

    /* continuous move listener */
    window.addEventListener('touchmove', function(e){
        e.preventDefault();
        var t = e.touches[0];
        swipe_det.eX = t.screenX;
        swipe_det.eY = t.screenY;
    }, false);

    /* touch end listener */
    window.addEventListener('touchend',function(e){
        if (( swipe_det.eX - min_x > swipe_det.sX || swipe_det.eX + min_x < swipe_det.sX ) &&
            ( swipe_det.eY < swipe_det.sY + max_y && swipe_det.sY > swipe_det.eY - max_y   &&
              swipe_det.eX > 0)){

            /* determine actual direction */
            if(swipe_det.eX > swipe_det.sX){
                direction = "r";
            }else{
                direction = "l";
            }
        }
        
        /* execute action if change was relevant */
        if (direction != "") {
            actionSwipe(direction)
        }

        /* reset direction in case listener is called again (it happens) */
        direction = "";

    }, false);
}

function actionSwipe(direction) {
    if(!window.location.href.includes("day-")){
        return
    }
    if(direction == "r"){
        window.location.assign(document.getElementById("prevDay").innerText)
    }
    if(direction == "l"){
        window.location.assign(document.getElementById("nextDay").innerText)
    }
}

addSwipeListeners();
window.addEventListener('online', goOnline);
window.addEventListener('offline', goOffline);
window.onload = runShit
