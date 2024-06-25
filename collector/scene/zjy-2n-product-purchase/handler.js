"use strict"

const request = require('./request-promise-uuid')

const constants = {
	URL_GETPRICE: process.env.URL_GETPRICE,
	URL_AUTHORIZECC: process.env.URL_AUTHORIZECC,
	URL_PUBLISH: process.env.URL_PUBLISH,
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

const api = {
	purchaseProduct: async (event, context, callback) => {
		console.log("Incoming event:");
		console.log(event);
		var authorizeCCData = event.body;

		const res = await request(functions.getRequestObject(authorizeCCData, constants.URL_AUTHORIZECC), constants.URL_AUTHORIZECC);
		callback(null, res);
	}
}

module.exports = (event, context, callback) => {
	console.log('abcd')
	api.purchaseProduct(event, context, callback);
}
