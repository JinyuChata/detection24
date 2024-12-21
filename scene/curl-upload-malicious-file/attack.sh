curl -X POST \
  http://localhost:31112/function/zjy-2n-product-purchase \
  -H "Content-Type: application/json" \
  -H "uuid: upload-malicious-file" \
  -d '{  
    "id": 1,
    "user": "alice",
    "creditCard": "1234-5678-9",
    "malicious": "uploadmaliciousfile",  
    "fileName": "bad_cmd.sh",  
    "fileContent": "touch ./uploads/bad_file.txt && echo bad > ./uploads/bad_file.txt && cat ./uploads/bad_file.txt"  
  }'