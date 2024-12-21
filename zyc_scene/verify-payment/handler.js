'use strict';

const request = require('./request-promise-uuid')

const constants = {
};

const functions = {
	getRequestObject: (requestVals, url) => {
		return {
			method: 'POST',
			uri: url,
			body: requestVals,
			json: true,
		}
	}
}

module.exports = async (event, context, callback) => {  
    try {  
        const res_verify_payment = {  
            "verify_payment": true  
        };  

        
        var result = {  
            ...res_verify_payment
        };  

        return callback(null, result);  
    } catch (error) { 
        return callback(null, { "err_verify_payment": error.message || "An unknown error occurred" });  
    }  
};

