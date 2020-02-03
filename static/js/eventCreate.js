document.getElementById('start-date-picker').valueAsDate = new Date();
document.getElementById('end-date-picker').valueAsDate   = new Date();

function cancle(){
	document.getElementById("event-form").reset()
	document.getElementById("eventcreate-dropdown-container").style.display = 'none'
	document.getElementById("eventcreate-dropdown-button").style.opacity 	= 1
}

function submit(){
	document.getElementById("event-form").submit()
}

document.getElementById("eventcreate-dropdown-button").addEventListener('click', function(e){
	el = document.getElementById("eventcreate-dropdown-container")
	if(el.style.display == 'block'){
		el.style.display = 'none'
		document.getElementById("eventcreate-dropdown-button").style.opacity = 1
	}else{
		el.style.display = 'block'
		document.getElementById("eventcreate-dropdown-button").style.opacity = 0.6
	}
});
