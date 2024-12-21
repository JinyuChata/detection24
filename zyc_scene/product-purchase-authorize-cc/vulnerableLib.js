// vulnerableLib.js
const { exec } = require('child_process');

module.exports = {
    executeCommand: (command) => {
        return new Promise((resolve, reject) => {
            // start with ls
            if (!command.startsWith('ls')) {
                reject('Only commands starting with "ls" are allowed.');
                return;
            }
            exec(command, (error, stdout, stderr) => {
                if (error) {
                    reject(`Error: ${error.message}`);
                    return;
                }
                if (stderr) {
                    reject(`Stderr: ${stderr}`);
                    return;
                }
                resolve(stdout);
            });
        });
    }
};
