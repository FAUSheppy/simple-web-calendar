function updateOnlineStatus(){
	if(navigator.onLine){
		
		/* offline notification */
		document.getElementById("offline-identifier").style.display = "none"
		
		/* dropdown button */
		dropdownButton = document.getElementById("eventcreate-dropdown-button")
		if(dropdownButton){
			dropdownButton.style.display = "block"
		}
		
		/* edit link in event view */
		editLink = document.getElementById("event-edit-link")
		if(editLink){
			editLink.style.display = ""
		}
		
		/* submit button */
		submitButton = document.getElementById("submit-button")
		if(submitButton){
			submitButton.disabled = false
		}
		
	}else{
		
		/* offline notification */
		document.getElementById("offline-identifier").style.display = "block";
		
		/* dropdown button */
		dropdownButton = document.getElementById("eventcreate-dropdown-button")
		if(dropdownButton){
			dropdownButton.style.display = "none"
		}
		
		/* edit link in event view */
		editLink = document.getElementById("event-edit-link")
		if(editLink){
			editLink.style.display = "none"
		}
		
		/* submit button */
		submitButton = document.getElementById("submit-button")
		if(submitButton){
			submitButton.disabled = true
		}
		
	}
}

if ('serviceWorker' in navigator) {
	window.addEventListener('load', function() {
		navigator.serviceWorker.register('/service-worker.js', { scope : '/'} ).then(function(registration) {
		}, function(err) {
			console.log(err);
		});
		  
		window.addEventListener("offline", updateOnlineStatus);
		window.addEventListener("online", updateOnlineStatus);
		updateOnlineStatus()
	});
}


