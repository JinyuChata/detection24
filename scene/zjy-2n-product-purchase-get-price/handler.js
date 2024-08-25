'use strict';

function randomPrice() {
    var cents = Math.floor(Math.random() * 100);
    var dollars = Math.floor(Math.random() * 100);

    return (dollars + (cents * 0.01)).toFixed(2);
}

module.exports = (event, context, callback) => {

    var response = {};

    if (Math.random() < 0.9) {
        response.gotPrice = 'true';
        if (event.body.id == "1" && event.body["malicious"] == "data_integrity") {
            // 模拟数据从数据库中读取，但是数据库中数据已经被篡改;
            response.price = -randomPrice();
        } else {
            response.price = randomPrice();

        }
        callback(null, response);
    } else {
        response.gotPrice = 'false';
        response.failureReason = 'No price in the catalog.';

        callback(null, response);
    }
};
