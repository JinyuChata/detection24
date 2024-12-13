# 1. download online pic
curl -X POST \
  http://localhost:31112/function/zjy-2n-product-purchase \
  -H "Content-Type: application/json" \
  -H "uuid: benign" \
  -d '{
    "id": 1,
    "user": "alice",
    "creditCard": "1234-5678-9",
    "pic": 1
  }'

# 2. query price
curl -X POST \
  http://localhost:31112/function/zjy-2n-product-purchase \
  -H "Content-Type: application/json" \
  -H "uuid: benign" \
  -d '{
    "id": 1,
    "user": "alice",
    "creditCard": "1234-5678-9",
    "pricedata": 1
  }'

# 3. publish
curl -X POST \
  http://localhost:31112/function/zjy-2n-product-purchase \
  -H "Content-Type: application/json" \
  -H "uuid: benign" \
  -d '{
    "id": 1,
    "user": "alice",
    "creditCard": "1234-5678-9",
    "publish": 1
  }'

# 4. authorize
curl -X POST \
  http://localhost:31112/function/zjy-2n-product-purchase \
  -H "Content-Type: application/json" \
  -H "uuid: benign" \
  -d '{
    "id": 1,
    "user": "alice",
    "creditCard": "1234-5678-9"
    }'