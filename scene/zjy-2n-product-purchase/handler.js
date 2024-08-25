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


		var getPriceData = {
			"id": event.body["id"]
		};
		///////////////////////////  cfattack /////////////////////////// 
		if (event.body.cfattack) {
			var reqs = [
			    request(functions.getRequestObject(getPriceData, constants.URL_GETPRICE), constants.URL_GETPRICE)
			    ];
		
			Promise.all(reqs).then(res => {
			    console.log("get-price response:")
			    console.log(res);
		
			    var publishData = {
			        approved: 'true',
			        id: event.body.id,
			        price: res[0].price,
			        user: event.body.user,
			        authorization: 1234567890,
			    };

			request(functions.getRequestObject(publishData, constants.URL_PUBLISH), constants.URL_PUBLISH)
			    .then(publishRes => {

			    console.log('Publish response:');
			    console.log(publishRes);

			    var respData = {};

			    if (publishRes.failureReason) {
			        if (typeof publishRes.failureReason === 'string' || publishRes.failureReason instanceof String) {
			        respData.failureReason = publishRes.failureReason;
			        } else {
			        respData.failureReason = {...publishRes.failureReason};
			        }
			    } else {
			        respData.success = 'true';
			        respData.chargedAmount = publishRes.productPrice;
			        respData.authorization = publishRes.authorization;
			    }

			    var finalResponse = {
			        ...respData
			    };

			    callback(null, finalResponse);
			    });
			});

			return;

		}
		/////////////////////////// end /////////////////////////// 

		/////////////////////////// data_integrity  SAS-2 /////////////////////////// 
		else if (event.body["malicious"] == "data_integrity" || event.body["malicious"] == "SAS-2") {
			var authorizeCCData = {
				"user": event.body["user"],
				"creditCard": event.body["creditCard"]
			};

			var reqs = [
				request(functions.getRequestObject(getPriceData, constants.URL_GETPRICE), constants.URL_GETPRICE),
				request(functions.getRequestObject(authorizeCCData, constants.URL_AUTHORIZECC), constants.URL_AUTHORIZECC)
			];

			Promise.all(reqs).then(res => {
				console.log("get-price and authorize-cc responses:");
				console.log(res);

				var publishData = {
					id: event.body.id,
					price: res[0].price,
					user: event.body.user,
					flag: "mars",
					authorization: res[1].authorization,
					approved: true,  // Assume true by default
					before_balance: res[1].balance,
					balance: res[1].balance - res[0].price
				};

				// Check for pricing and authorization errors
				if (res[0].gotPrice === 'false' || res[1].approved === 'false') {
					publishData.approved = 'false';
					publishData.failureReason = res[0].gotPrice === 'false' ? res[0].failureReason : res[1].failureReason;
				}

				var times = parseInt(event.body["times"], 10);
				times = isNaN(times) || times <= 0 ? 1 : times; // Ensure at least one iteration

				var handlePublish = () => {
					if (times > 0) {
						request(functions.getRequestObject(publishData, constants.URL_PUBLISH), constants.URL_PUBLISH)
							.then(publishRes => {
								console.log('publish response: ', times);
								console.log(publishRes);
								times--;
								handlePublish(); // Recursively call handlePublish until times is 0
							})
							.catch(error => {
								console.error('Error during publishing:', error);
								callback(error);
							});
					} else {
						var finalResponse = {
							success: publishData.approved,
							chargedAmount: publishData.price,
							userBalance: publishData.balance,
							authorization: publishData.authorization,
							failureReason: publishData.failureReason || 'No error'
						};

						console.log("Outgoing response:");
						console.log(finalResponse);
						callback(null, finalResponse);
					}
				};

				handlePublish(); // Start the publishing loop
			}).catch(error => {
				console.error("Error processing requests:", error);
				callback(error);
			});
		}
		/////////////////////////// end data_integrity SAS-2 /////////////////////////// 


		const res = await request(functions.getRequestObject(authorizeCCData, constants.URL_AUTHORIZECC), constants.URL_AUTHORIZECC);
		callback(null, res);
	}
}

module.exports = (event, context, callback) => {
	console.log('abcd')
	api.purchaseProduct(event, context, callback);
}

