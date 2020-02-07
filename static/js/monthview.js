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
    year = date.getFullYear()
    if(window.location.href.includes("month=" + month) && window.location.href.includes("year=" + year)){
        element = document.getElementById("day-"+date.getDate())
        if(element){
          element.style.background = "orange"
        }
    }

}

/* execute defered operations */
setCurrentDate()
highlightCurrentDay()
