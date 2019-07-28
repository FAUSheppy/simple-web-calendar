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
