#!/bin/bash

# Файл со списком ссылок на swagger.js
input_file="swagger_js.txt"

# Папка для результатов ZAP
mkdir -p zap_reports

while IFS= read -r url; do
    # Сначала конвертируем js -> json
    python3 swaggerjs2json.py -d "$url"

    # Получаем домен из URL для имени отчета и пути к json
    domain=$(echo "$url" | awk -F[/:] '{print $4}')
    json_file="${domain}.json"
    report_file="zap_reports/report_${domain}.html"

    # Запуск ZAP API scan
    docker run -v "$(pwd)":/zap/wrk/:rw -t zaproxy/zap-stable \
        zap-api-scan.py -t "/zap/wrk/${json_file}" -O "https://${domain}" -f openapi -r "${report_file}"

    echo "[+] Отчет создан: ${report_file}"
done < "$input_file"
