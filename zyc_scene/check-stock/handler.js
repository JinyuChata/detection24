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
        const res_check_stock = {  
            "check_stock": true  
        };  

        
        var result = {  
            ...res_check_stock
        };  

        return callback(null, result);  
    } catch (error) { 
        return callback(null, { "err_check_stock": error.message || "An unknown error occurred" });  
    }  
};

