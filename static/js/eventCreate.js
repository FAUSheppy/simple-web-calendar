document.getElementById('start-date-picker').valueAsDate = new Date();
document.getElementById('end-date-picker').valueAsDate   = new Date();

function cancle(){
	document.getElementById("event-form").reset()
	document.getElementById("eventcreate-dropdown-container").style.visibility = 'hidden'
	document.getElementById("eventcreate-dropdown-container").style.opacity = 0
	document.getElementById("eventcreate-dropdown-button").style.opacity 	= 1
}

function submit(){
	document.getElementById("event-form").submit()
}

document.getElementById("eventcreate-dropdown-button").addEventListener('click', function(e){
	el = document.getElementById("eventcreate-dropdown-container")
	if(el.style.visibility == 'visible'){
		el.style.opacity = 0
		el.style.visibility = 'hidden'
		document.getElementById("eventcreate-dropdown-button").style.opacity = 1
	}else{
		el.style.visibility = 'visible'
		el.style.opacity = 1
		document.getElementById("eventcreate-dropdown-button").style.opacity = 0.6
	}
});
