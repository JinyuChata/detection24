'use strict';

const request = require('./request-promise-uuid')

const constants = {
	URL_VALIDATE_CART: process.env.URL_VALIDATE_CART,
    URL_CREATE_ORDER: process.env.URL_CREATE_ORDER,
    URL_PROCESS_PAYMENT: process.env.URL_PROCESS_PAYMENT,
    URL_UPDATE_STOCK: process.env.URL_UPDATE_STOCK
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
        const res_place_order = {  
            "place_order": true  
        };  
 
        const res_validate_cart = await request(functions.getRequestObject(event.body, constants.URL_VALIDATE_CART), constants.URL_VALIDATE_CART);
        if (Math.random() < 0.4) {  
            return callback(null, { "place_order": false });  
        }    
        const res_create_order = await request(functions.getRequestObject(event.body, constants.URL_CREATE_ORDER), constants.URL_CREATE_ORDER);
        if (Math.random() < 0.2) {  
            return callback(null, { "place_order": false });  
        }    
        const res_process_payment = await request(functions.getRequestObject(event.body, constants.URL_PROCESS_PAYMENT), constants.URL_PROCESS_PAYMENT);
        if (Math.random() < 0.3) {  
            return callback(null, { "place_order": false });  
        }  
        const res_update_stock = await request(functions.getRequestObject(event.body, constants.URL_UPDATE_STOCK), constants.URL_UPDATE_STOCK);
        
        var result = {  
            ...res_place_order,  
            ...res_validate_cart,  
            ...res_create_order,
            ...res_process_payment,
            ...res_update_stock  
        };  

        return callback(null, result);  
    } catch (error) { 
        return callback(null, { "err_place_order": error.message || "An unknown error occurred" });  
    }  
};

