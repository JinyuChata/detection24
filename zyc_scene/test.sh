curl -X POST \
  http://localhost:31112/function/product-purchase \
  -H "Content-Type: application/json" \
  -H "uuid: test" \
  -d '{
    "id": 1,
    "user": "alice",
    "creditCard": "1234-5678-9",
    "test": "place-order"
  }'