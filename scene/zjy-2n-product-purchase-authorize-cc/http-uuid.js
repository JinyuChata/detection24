const http = require("http");
const { get_uuid } = require("./express-new");

function get(...args) {
    var uuid = get_uuid();
    if (!uuid) {
        return http(...args);
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

    return http.get(...args);
}

module.exports = {get}
