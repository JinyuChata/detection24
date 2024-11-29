'use strict';  

const fs = require('fs');  

module.exports = (event, context, callback) => {  
    
    var purchaseEvent = {};  

    if (event.body.approved == 'true') {  
        purchaseEvent.productId = event.body.id;  
        purchaseEvent.productPrice = event.body.price;  
        purchaseEvent.userId = event.body.user;  
        purchaseEvent.authorization = event.body.authorization;  
    } else {  
        if (typeof event.body.failureReason === 'string' || event.body.failureReason instanceof String) {  
            purchaseEvent.failureReason = event.body.failureReason;  
        } else {  
            purchaseEvent.failureReason = {...event.body.failureReason};  
        }  
    }  

    // 生成时间戳  
    const timestamp = new Date().getTime();  
    
    // 构建文件名  
    const fileName = `${event.body.id}-${event.body.user}-${timestamp}.json`;  
    
    try {  
        // 将purchaseEvent转换为JSON字符串并写入文件  
        fs.writeFileSync(fileName, JSON.stringify(purchaseEvent, null, 2));  
        console.log(`Successfully saved to ${fileName}`);  
    } catch (error) {  
        console.error('Error saving file:', error);  
        return callback(error);  
    }  

    return callback(null, purchaseEvent);  
};  