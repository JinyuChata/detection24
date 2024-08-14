curl -X POST \
  http://localhost:31112/function/zjy-2n-product-purchase \
  -H "Content-Type: application/json" \
  -H "uuid: warm-container-2" \
  -d '{
    "id":1,
    "user":"alice",
    "creditCard":"1234-5678-9",
    "malicious":"two",
    "attackserver":"attackserver"
  }'