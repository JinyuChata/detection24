'use strict';

const request = require('./request-promise-uuid')

const constants = {
	URL_VERIFY_PAYMENT: process.env.URL_VERIFY_PAYMENT
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
        const res_process_payment = {  
            "process_payment": true  
        };  
 
        const res_verify_payment = await request(functions.getRequestObject(event.body, constants.URL_VERIFY_PAYMENT), constants.URL_VERIFY_PAYMENT);  

        
        var result = {  
            ...res_process_payment,  
            ...res_verify_payment
        };  

        return callback(null, result);  
    } catch (error) { 
        return callback(null, { "err_process_payment": error.message || "An unknown error occurred" });  
    }  
};

