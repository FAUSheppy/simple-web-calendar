var ical = require("ical.js")
var dav  = require('dav')


dav.debug.enabled = true

function handleInput(){

    /* parse input */
    // startdate
    // duration
    // description
    // location
    // category
    // DEBUG_IDENTIFIER

    /* define event from input */
    var eventDefinition = {
        // ...
    }

    /* create client object */
    var auth      = new dav.Credentials({username: 'xxx', password: 'xxx'})
    var transport = new dav.transport.Basic(auth)
    var client    = new dav.Client(transport, {baseUrl: 'https://mail.mozilla.com'})

    /* create function to handle response */
    var responseHandler = function(response) {
                              console.log(response)
                          }

    /* create event from definition */
    ics.createEvent(event, (error, vEvent) => {
        
        /* fail or error */
        if (error) {
            console.log(error)
            return
        }

        /* send VEvent to server */
        client.send(vEvent, "/test/test.ics").then(responseHandler)


    })

}
