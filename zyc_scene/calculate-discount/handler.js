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
        const res_calculate_discount = {  
            "calculate_discount": true  
        };  

        
        var result = {  
            ...res_calculate_discount
        };  

        return callback(null, result);  
    } catch (error) { 
        return callback(null, { "err_calculate_discount": error.message || "An unknown error occurred" });  
    }  
};

