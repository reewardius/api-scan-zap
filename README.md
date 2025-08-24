# api-scan-zap

Get swagger api endpoints
```
subfinder -dL root.txt -all -silent -o subs.txt && \
naabu -l subs.txt -s s -tp 100 -ec -c 50 -o naabu.txt && \
httpx -l naabu.txt -rl 500 -t 200 -o alive_http_services.txt && \
nuclei -l alive_http_services.txt -t swagger.yaml -rl 1000 -c 100 -o swagger_endpoints.txt
```

Filter swagger json and swagger js endpoints
```
cat swagger_endpoints.txt | grep json | awk '{for(i=1;i<=NF;i++) if($i ~ /^https?:\/\//) print $i}' > swagger_json.txt
cat swagger_endpoints.txt | grep ui-init | awk '{for(i=1;i<=NF;i++) if($i ~ /^https?:\/\//) print $i}' > swagger_js.txt
```

Run API scanning with the Swagger JSON file located on the website
```
# targets located in swagger_json.txt file

docker run -v $(pwd):/zap/wrk/:rw -t zaproxy/zap-stable zap-api-scan.py -t https://target.com/swagger.json -f openapi -r report.html
```
---
Convert JS 2 Swagger JSON format
```
# js targets located in swagger_js.txt file

python swaggerjs2json.py -d https://target.com/api/swagger/swagger-ui-init.js

[+] Скачиваем https://target.com/api/swagger/swagger-ui-init.js -> target.com.js
[+] Swagger сохранен в target.com.json
[+] Удален временный файл target.com.js

or u can use -f arg with swagger_js.txt links

python swaggerjs2json.py -f swagger_js.txt
```

Run API scan with a local JSON file (after conversion from JS format)
```
docker run -v $(pwd):/zap/wrk/:rw -t zaproxy/zap-stable zap-api-scan.py -t /zap/wrk/target.com.json -O https://target.com -f openapi -r report.html
```
