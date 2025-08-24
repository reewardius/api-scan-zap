import re
import json
import sys
import os
import requests
from urllib.parse import urlparse
import argparse

def download_file(url):
    domain = urlparse(url).netloc
    local_filename = f"{domain}.js"
    print(f"[+] Скачиваем {url} -> {local_filename}")
    resp = requests.get(url)
    resp.raise_for_status()
    with open(local_filename, "w", encoding="utf-8") as f:
        f.write(resp.text)
    return local_filename, domain

def extract_swagger_doc(data):
    start_pattern = r'"swaggerDoc"\s*:\s*\{'
    start_match = re.search(start_pattern, data)
    if not start_match:
        raise ValueError("Не удалось найти начало swaggerDoc в файле")
    start_pos = start_match.start() + len(start_match.group()) - 1
    brace_count = 0
    pos = start_pos
    in_string = False
    escape_next = False
    while pos < len(data):
        char = data[pos]
        if escape_next:
            escape_next = False
        elif char == '\\':
            escape_next = True
        elif char == '"' and not escape_next:
            in_string = not in_string
        elif not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    break
        pos += 1
    if brace_count != 0:
        raise ValueError("Не удалось найти закрывающую скобку для swaggerDoc")
    return data[start_pos:pos + 1]

def fix_json_issues(json_str):
    fixed = re.sub(r',(\s*[}\]])', r'\1', json_str)
    fixed = re.sub(r'//.*?\n', '\n', fixed)
    fixed = re.sub(r'/\*.*?\*/', '', fixed, flags=re.DOTALL)
    return fixed

def validate_and_enhance_swagger(swagger_doc, domain):
    if 'openapi' not in swagger_doc:
        swagger_doc['openapi'] = '3.0.0'
    if 'info' not in swagger_doc:
        swagger_doc['info'] = {'title': 'API Documentation', 'version': '1.0.0'}
    if 'title' not in swagger_doc['info']:
        swagger_doc['info']['title'] = 'API Documentation'
    if 'version' not in swagger_doc['info']:
        swagger_doc['info']['version'] = '1.0.0'
    if 'servers' not in swagger_doc or not swagger_doc['servers']:
        swagger_doc['servers'] = [{'url': f'https://{domain}', 'description': 'Server'}]
    if 'paths' not in swagger_doc:
        swagger_doc['paths'] = {}
    paths_to_remove = [p for p, m in swagger_doc['paths'].items() if not isinstance(m, dict) or not m]
    for path in paths_to_remove:
        del swagger_doc['paths'][path]
    for path, methods in swagger_doc['paths'].items():
        for method, details in methods.items():
            if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                if 'responses' not in details:
                    details['responses'] = {'200': {'description': 'Successful response'}}
                for status_code, response in details.get('responses', {}).items():
                    if 'description' not in response:
                        response['description'] = f'Response {status_code}'
    return swagger_doc

def process_url(url):
    local_file = None
    try:
        local_file, domain = download_file(url)
        with open(local_file, "r", encoding="utf-8") as f:
            data = f.read()
        swagger_doc_str = extract_swagger_doc(data)
        fixed_json_str = fix_json_issues(swagger_doc_str)
        swagger_doc = json.loads(fixed_json_str)
        enhanced_doc = validate_and_enhance_swagger(swagger_doc, domain)
        output_file = f"{domain}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(enhanced_doc, f, indent=2, ensure_ascii=False)
        print(f"[+] Swagger сохранен в {output_file}")
    except Exception as e:
        print(f"[!] Ошибка обработки {url}: {e}")
    finally:
        if local_file and os.path.exists(local_file):
            os.remove(local_file)
            print(f"[+] Удален временный файл {local_file}")

def main():
    parser = argparse.ArgumentParser(description="Конвертация swagger.js в swagger.json")
    parser.add_argument("-d", "--direct", help="Прямая ссылка на swagger.js")
    parser.add_argument("-f", "--file", help="Файл со списком ссылок на swagger.js")
    args = parser.parse_args()

    urls = []
    if args.direct:
        urls.append(args.direct)
    if args.file:
        if not os.path.exists(args.file):
            print(f"[!] Файл {args.file} не найден")
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    urls.append(line)

    if not urls:
        print("[!] Не указаны ссылки на swagger.js")
        sys.exit(1)

    for url in urls:
        process_url(url)

if __name__ == "__main__":
    main()
