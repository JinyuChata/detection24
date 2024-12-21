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
        const res_update_stock = {  
            "update_stock": true  
        };  

        
        var result = {  
            ...res_update_stock
        };  

        return callback(null, result);  
    } catch (error) { 
        return callback(null, { "err_update_stock": error.message || "An unknown error occurred" });  
    }  
};

