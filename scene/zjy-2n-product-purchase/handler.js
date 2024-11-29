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

		///////////////////////////  cfattack /////////////////////////// 
		var getPriceData = {
			"id": event.body["id"]
		};
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
		} else if (event.body.pricedata) {
			// query price ...
			const res = await request(functions.getRequestObject(getPriceData, constants.URL_GETPRICE), constants.URL_GETPRICE);
			callback(null, res);
		} else if (event.body.publish) {
			// publish purchase ...
			var publishData = {
				approved: 'true',
				id: event.body.id,
				price: 0.1,
				user: event.body.user,
				authorization: 1234567890,
			};
			const res = await request(functions.getRequestObject(publishData, constants.URL_PUBLISH), constants.URL_PUBLISH);
			res['status'] = "PUBLISHED";
			callback(null, res);
		} else if (event.body.pic) {
			// download pic and return
			// TODO: download https://cse2021-dune.oss-cn-beijing.aliyuncs.com/202411291115746.png image and return to client
			try {  
				const imageUrl = 'https://cse2021-dune.oss-cn-beijing.aliyuncs.com/202411291115746.png';  
				const options = {  
					method: 'GET',  
					url: imageUrl,  
					encoding: null,  // 重要：使用 null 来获取 buffer  
					resolveWithFullResponse: true  // 获取完整响应，包括 headers  
				};  
			
				const response = await request(options);  
				// 将图片数据转换为Base64  
				const base64Image = Buffer.from(response.body).toString('base64');  
				
				callback(null, {  
					statusCode: 200,  
					headers: {  
						'Content-Type': 'application/json'  
					},  
					body: {  
						image: base64Image,  
						contentType: response.headers['content-type']  
					}  
				});  
			} catch (error) {  
				console.error('Error downloading image:', error);  
				callback(null, {  
					statusCode: 500,  
					body: {  
						error: 'Failed to download image',  
						message: error.message  
					}  
				});  
			}  
		} else {
			// purchase ...
			const res = await request(functions.getRequestObject(authorizeCCData, constants.URL_AUTHORIZECC), constants.URL_AUTHORIZECC);
			callback(null, res);
		}
		/////////////////////////// end /////////////////////////// 


	}
}

module.exports = (event, context, callback) => {
	console.log('abcd')
	api.purchaseProduct(event, context, callback);
}
