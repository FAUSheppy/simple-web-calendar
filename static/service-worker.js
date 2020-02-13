var CACHE = 'cache';

// function buildPrecacheRequestParameters(){
	// current =  location.href
	// urlParams = new URLSearchParams(location.search)
	// if(current.includes("monthview")){
		// month = urlParams.get("month")
		// year  = urlParams.get("year")
		// return "?year=" + year + "&month=" + month
	// }else if(current.includes("dayview")){
		// day   = urlParams.get("day")
		// month = urlParams.get("month")
		// year  = urlParams.get("myear")
		// return "?year=" + year + "&month=" + month + "&day=" + day
	// }else if(current.includes("eventview")){
		// uid   = urlParams.get("uid")
    	// return "?dummy=True"
	// }else{
    	// return "?dummy=True"
	// }
// }

function requestPrecacheUrls(target){
    requestURL = target + "?server-decides=True" //+ buildPrecacheRequestParameters()
	fetch(requestURL).then(
		function(response) {
			if (response.status == 200) {
				response.json().then((data) => {
					data.forEach(url => {
						caches.open(CACHE).then(function (cache){
							fetch(url).then(function(responseForPrecache){
								cc = responseForPrecache.headers.get("Cache-Control")
								if(cc && cc.includes("no-cache")){
									return
								}
								cache.put(url, responseForPrecache.clone())
							})
						});
					});
				});
			}else{
				console.log(requestURL, response.status)
			}
		}
	)
}

self.addEventListener('install', function(event) {
	requestPrecacheUrls("/get-dynamic-precache")
	requestPrecacheUrls("/get-static-precache")
});

/* fetch */
function fromNetwork(request, timeout) {
	if(request.url.includes("precache")){
		return
	}
	return new Promise(function (fulfill, reject) {
		var timeoutId = setTimeout(reject, timeout);
		caches.open(CACHE).then(function(cache){
			fetch(request).then(function(response) {
				cc = response.headers.get("Cache-Control")
				if(cc && cc.includes("no-cache")){
					fulfill(response)
					return
				}
				cache.put(request, response.clone()).then(function () {
					fulfill(response);
				});
			}, reject);
		});
	});
}

function fromCache(request) {
	const cacheRequestFailed = new Response("You are offline and the requested Page failed. Use Back Button To Return", {"status" : 408, "headers" : {"Content-Type" : "text/plain"}});
	return caches.open(CACHE).then(function (cache) {
		return cache.match(request).then(function(matching){
			if(matching){
				return matching
			}else{
				return cacheRequestFailed
			}
		})
	})
}

self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim());
});

// function periodicReload(){
	// requestPrecacheUrls("/get-dynamic-precache")
	// requestPrecacheUrls("/get-static-precache")
// }

// setInterval(periodicReload, 10000);

self.addEventListener('fetch', function(evt){
	evt.respondWith(fromNetwork(evt.request, 2000).catch(() => { return fromCache(evt.request) }))
});
