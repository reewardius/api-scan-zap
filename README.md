# api-scan-zap

Get swagger json endpoints
```
nuclei -l alive_http_services_advanced.txt -t swagger.yaml -rl 1000 -c 100 -o swagger_endpoints.txt
```

Filter swagger json and swagger js endpoints
```
cat swagger_endpoints.txt | grep json | awk '{for(i=1;i<=NF;i++) if($i ~ /^https?:\/\//) print $i}' > swagger_json.txt
cat swagger_endpoints.txt | grep ui-init | awk '{for(i=1;i<=NF;i++) if($i ~ /^https?:\/\//) print $i}' > swagger_js.txt
```

Convert JS 2 Swagger JSON format
```
python swaggerjs2json.py -f swagger_js.txt
```

Run API scanning with the Swagger JSON file located on the website
```
docker run -v $(pwd):/zap/wrk/:rw -t zaproxy/zap-stable zap-api-scan.py -t https://target.com/swagger.json -f openapi -r report.html
```

Run API scan with a local JSON file (after conversion from JS format)
```
docker run -v $(pwd):/zap/wrk/:rw -t zaproxy/zap-stable zap-api-scan.py -t /zap/wrk/target.com.json -O https://target.com -f openapi -r report.html
```
