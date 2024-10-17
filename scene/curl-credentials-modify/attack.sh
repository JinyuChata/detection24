curl -X POST \
  http://localhost:31112/function/zjy-alastor-2n-product-purchase \
  -H "Content-Type: application/json" \
  -H "uuid: credentials-modify-attack-2" \
  -d '{
    "id": 1,
    "user": "alice",
    "creditCard": "1234-5678-9",
    "malicious": "sas3",
    "fileName": "2.txt #\n echo '123' > 3.txt"
  }'