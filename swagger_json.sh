#!/bin/bash

# файл со списком swagger URL
input_file="swagger_json.txt"

while IFS= read -r target; do
    # получить домен из URL для имени отчета
    domain=$(echo "$target" | awk -F[/:] '{print $4}')
    report_file="report_${domain}.html"
    
    # запуск Docker с ZAP
    docker run -v "$(pwd)":/zap/wrk/:rw -t zaproxy/zap-stable \
        zap-api-scan.py -t "$target" -f openapi -r "$report_file"
done < "$input_file"
