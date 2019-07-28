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

function functionLoadUpcomingEvents(){

    if(window.location.href.includes("month-")){
      link = "/day-" + date.getFullYear()   + "&" +
                       monthStr             + "&" +
                       date.getDate()       + ".html"
      var xhttp = new XMLHttpRequest();
      xhttp.onreadystatechange = append;
      xhttp.open("GET", link, true);
      xhttp.send();
    }

    /* create pseudo doc for selection */
    var doc = new DOMParser().parseFromString(this.responseText,"text/html")

    if(!doc.body.innerHTML){
        return
    }

    var menubar = doc.getElementsByClassName("menubar")[0]
    menubar.innerText = "Heute"

    var elem = doc.getElementById("menubarDate");
    elem.parentNode.removeChild(elem);

    /* put it together */
    document.body.innerHTML += doc.body.innerHTML
}

/* execute defered operations */
setCurrentDate()
