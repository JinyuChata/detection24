'use strict';

const request = require('./request-promise-uuid')

const constants = {
	URL_CALCULATE_DISCOUNT: process.env.URL_CALCULATE_DISCOUNT
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
        const res_create_order = {  
            "create_order": true  
        };  
 
        const res_calculate_discount = await request(functions.getRequestObject(event.body, constants.URL_CALCULATE_DISCOUNT), constants.URL_CALCULATE_DISCOUNT);  

        
        var result = {  
            ...res_create_order,  
            ...res_calculate_discount
        };  

        return callback(null, result);  
    } catch (error) { 
        return callback(null, { "err_create_order": error.message || "An unknown error occurred" });  
    }  
};

