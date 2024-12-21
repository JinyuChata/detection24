'use strict';

const request = require('./request-promise-uuid')

const constants = {
	URL_CHECK_STOCK: process.env.URL_CHECK_STOCK
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
        const res_validate_cart = {  
            "validate_cart": true  
        };  
 
        const res_check_stock = await request(functions.getRequestObject(event.body, constants.URL_CHECK_STOCK), constants.URL_CHECK_STOCK);  

        
        var result = {  
            ...res_validate_cart,  
            ...res_check_stock
        };  

        return callback(null, result);  
    } catch (error) { 
        return callback(null, { "err_validate_cart": error.message || "An unknown error occurred" });  
    }  
};

