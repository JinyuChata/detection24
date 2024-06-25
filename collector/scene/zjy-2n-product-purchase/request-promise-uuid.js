const request = require('request-promise')
const { get_uuid } = require('./express-new')
// requestWithUUID is the wrapper of request-promise
function requestWithUUID(...args) {
    /*
        const request = require('request-promise')
        1. request(uri)
        2. request(uri, options)
        3. request(options)
        4. request(uri, callback)
        5. request(uri, options, callback)
        6. request(options, callback)
    */
    var uuid = get_uuid();
    if (!uuid) {
        return request(...args);
    }
    var index = -1;
    for (let i = 0; i < args.length; i++) {
        if (i > 2) { // ignore other args
            break;
        }
        if (args[i] !== null && typeof args[i] === 'object') {  // find the first object in args, it's the options
            index = i;
            break;
        }
    }
    if (index != -1) {  // find the options
        const options = args[index];
        if (options.headers) {
            options.headers['uuid'] = uuid;
        } else {
            options.headers = {'uuid': uuid};
        }
        
    } else {
        // can't find the options, add options arg
        var options = {
            headers:{'uuid': uuid}
        }
        args.splice(1, 0, options); // add options at index 1
    }

    return request(...args);
}

// function requestWithUUID(options) {
//     var uuid = httpContext.get("uuid");
//     options.headers = {'uuid': uuid}
//     return request(options);
// }

module.exports = requestWithUUID