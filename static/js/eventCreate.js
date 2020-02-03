document.getElementById('start-date-picker').valueAsDate = new Date();
document.getElementById('end-date-picker').valueAsDate   = new Date();

function toggleDropdown(){
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
}

function isStartGreaterEnd(){
	startDate = document.getElementById("start-date-picker")
	startTime = document.getElementById("start-time-picker")
	endDate   = document.getElementById("end-date-picker")
	endTime   = document.getElementById("end-time-picker")
	
	start = new Date(startDate.value + ":" + startTime.value)
	end   = new Date(endDate.value   + ":" + endTime.value)
	return start > end
}

function checkStartDate(event){
	if(isStartGreaterEnd()){
		startDate.value = endDate.value
		startTime.value = ""
	}
}
function checkEndDate(event){
	if(isStartGreaterEnd()){
		endDate.value = startDate.value
		endTime.value = startTime.value
	}
}

function cancle(){
	document.getElementById("event-form").reset()
	toggleDropdown()
}

function submit(){
	document.getElementById("event-form").submit()
	document.getElementById("event-form").reset()
	toggleDropdown()
}

document.getElementById("eventcreate-dropdown-button").addEventListener('click', function(e){
	toggleDropdown()
});
