import time
import requests
import re
from urllib.parse import quote, quote_plus, urlencode

    # === Settings === ***************************************
filename = "payloads"
payloads="""
'
"
"""
raw_request = """GET /FUZZ HTTP/1.1
Host: 127.0.0.1
Cookie: session=XYBkJt64Sgg1MKF26DPTzlCOkKGOTX2F
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3
Accept-Encoding: gzip, deflate, br, zstd
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Sec-Fetch-User: ?1
If-Modified-Since: Thu, 10 Jul 2025 02:55:21 GMT
If-None-Match: "29af-6398a5308a0b5-gzip"
Priority: u=0, i

"""


# === Functions === ***************************************
def main():    
    # load payloads
    payloads_list = _payloads(payloads, filename, debug=1)
    # skeleton for future use (bypass support)
    payloads_list_baypas = payloads_list
    # encode payloads, options: url, url+, urlen, none
    code_payloads = _code_payloads(payloads_list_baypas, "none", debug=0)
  
    #
    request=_list_request(raw_request,debug=0)
    #
    final_requests=_list_request_and_payloads( code_payloads,request,debug=0) 
    #
    ideal_request=_ideal_request(raw_request,debug=0)
 

    scheme=_get_scheme_from_request(ideal_request,debug=0)
    #
    method=_get_method_from_request(ideal_request, debug=0) 
    full_url=_get_full_url_from_request(ideal_request, scheme=scheme, debug=0)  
    headers=_get_headers_from_request(ideal_request, debug=0) 
    cookies=_get_cookies_from_request(ideal_request, debug=0)
    data=_get_data_from_request(ideal_request, debug=0)
    

    ideal_elapsed, ideal_status, ideal_content_len, ideal_response=_send_request(method, full_url, headers, cookies, data,timeout=10, debug=0)  
    print("Ideal request")
    print(f"               {ideal_elapsed}sec, cod:{ideal_status}, len:,{ideal_content_len} ")


    print("Requests with payloads")
    for i, r in enumerate(final_requests, 0):
        method=_get_method_from_request(r, debug=0) 
        full_url=_get_full_url_from_request(r, scheme=scheme, debug=0)  
        headers=_get_headers_from_request(r, debug=0) 
        cookies=_get_cookies_from_request(r, debug=0)
        data=_get_data_from_request(r, debug=0)

        elapsed, status, content_len, response=_send_request(method, full_url, headers, cookies, data,timeout=10, debug=0)  
        
        print(f"               {elapsed}sec, cod:{status}, len:,{content_len} ")



def _send_request(method, url, headers, cookies, data, timeout, debug):
    try:
        start = time.time()
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            cookies=cookies,
            data=data,
            timeout=timeout  
        )
        end = time.time()
    except requests.exceptions.RequestException as e:
        if debug:
            print(f"[DEBUG] drop of timeout: {e}")
        return timeout, "drop", 0, ""
    elapsed = round(end - start, 2)
    content_len = len(response.content)
    status = response.status_code

    if debug:
        print(f"[DEBUG] Код ответа: {status}")
        print(f"[DEBUG] Время ответа: {elapsed:.3f} сек")
        print(f"[DEBUG] Длина ответа: {content_len}")
        print('\n')
        #print(response.text)

    return elapsed, status, content_len, response.text

def _get_data_from_request(request_lines, debug=0):
    if not request_lines or not isinstance(request_lines, list):
        return None

    # # Convert to a single string and split by double newline
    raw = request_lines[0]
    parts = raw.split("\n\n", 1)

    if len(parts) == 2:
        body = parts[1].strip()
        if debug:
            print(f"[DEBUG] Find Data:")
            print(f"              {body}")
        return body if body else None

    if debug:
        print("[DEBUG] Not find Data.")
    return None

def _get_headers_from_request(request_lines, debug=0):
    if not request_lines or not isinstance(request_lines[0], str):
        return {}

    raw = request_lines[0]
    lines = raw.split("\n")
    if debug:
        print(f"[DEBUG] headers:")
    headers = {}
    for line in lines[1:]:  
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if key.lower() != 'cookie':
                headers[key] = value
                if debug:
                    print(f"              {key} = {value}")
    

    return headers

def _get_scheme_from_request(ideal_request, debug=0):
    # Convert to a list of strings
    if isinstance(ideal_request, str):
        ideal_request = ideal_request.splitlines()
    elif isinstance(ideal_request, list):
        lines = []
        for item in ideal_request:
            lines.extend(item.splitlines())
        ideal_request = lines

    scheme = "http"

    for line in ideal_request:
        stripped = line.strip().lower()
        if stripped.startswith("x-forwarded-proto:") and "https" in stripped:
            scheme = "https"
        elif stripped.startswith("forwarded:") and "proto=https" in stripped:
            scheme = "https"
        elif "https://" in stripped:
            scheme = "https"

    if debug:
        print("DEBUG scheme:", scheme)
    return scheme

def _get_full_url_from_request(ideal_request, scheme="", debug=0):
    """
    найдена ошибка если в куки добавить пайлоад, он не будет использоваться..
    сменить нейменг
    """
    if isinstance(ideal_request, str):
        ideal_request = ideal_request.splitlines()
    elif isinstance(ideal_request, list):
        lines = []
        for item in ideal_request:
            lines.extend(item.splitlines())
        ideal_request = lines

    path = None
    host = None

    for line in ideal_request:
        stripped = line.strip()
        if not path:
            parts = stripped.split()
            if len(parts) >= 2 and parts[0].upper() in {"GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"}:
                path = parts[1]
        if not host and stripped.lower().startswith("host:"):
            host = stripped[len("host:"):].strip()

    if path and host:
        full_url = f"{scheme}://{host}{path}"
        if debug:
            print("DEBUG full_url:", full_url)
        return full_url
    return None

def _get_method_from_request(ideal_request, debug=0):
    # Convert to a list of strings
    if isinstance(ideal_request, str):
        ideal_request = ideal_request.splitlines()
    elif isinstance(ideal_request, list):
        lines = []
        for item in ideal_request:
            lines.extend(item.splitlines())
        ideal_request = lines

    for line in ideal_request:
        stripped = line.strip()
        if stripped:  
            parts = stripped.split()
            if len(parts) >= 1:
                method = parts[0].upper()
                if debug:
                    print("DEBUG method:", method)
                return method
    return None  

def _get_cookies_from_request(ideal_request, debug=0):    
    if isinstance(ideal_request, str):
        ideal_request = ideal_request.splitlines()
    elif isinstance(ideal_request, list):        
        lines = []
        for item in ideal_request:
            lines.extend(item.splitlines())
        ideal_request = lines

    cookies = {}
    for line in ideal_request:
        stripped = line.strip()
        if stripped.lower().startswith("cookie:"):
            cookie_line = stripped[len("cookie:"):].strip()
            for pair in cookie_line.split(";"):
                if "=" in pair:
                    k, v = pair.strip().split("=", 1)
                    cookies[k] = v
    if debug:
        print("DEBUG cookies:", cookies)
    return cookies

def _ideal_request(raw_request, debug=0):
    cleaned = raw_request.replace("FUZZ", "")
    result = [cleaned]
    if debug:
        print(result[0])
    return result

def _list_request_and_payloads(payloads,request,debug=0):    
    result = []
    for payload in payloads:
        modified_request = [line.replace("{{PAYLOAD}}", payload) for line in request]
        result.append(modified_request)
        if debug:
            print("\n".join(modified_request))
    return result

def _list_request(raw_request, debug=0):
    """
    # Processes a raw HTTP request containing multiple FUZZ markers.
    # Returns:
    #   - list of full requests with {{PAYLOAD}} substitution
    #   - HTTP method (GET, POST, etc.)
    #   - empty string for cookies (reserved for future use)

    """
    result = []

    positions = [m.start() for m in re.finditer("FUZZ", raw_request)]

    if not positions:
        return [raw_request], "", ""
    
    for i, pos in enumerate(positions):
        temp = raw_request[:pos] + "{{PAYLOAD}}" + raw_request[pos + len("FUZZ"):]
        temp = temp.replace("FUZZ", "")  
        result.append(temp)

  
    if debug != 0:
        #print(f"[DEBUG] Метод запроса: {method}")
        print(f"[DEBUG] Найдено FUZZ: {len(positions)}")
        for i, r in enumerate(result):
            print(f"\n--- Вариант #{i+1} ---\n{r}")

    return result

def _payloads(payloads,filename,debug=0):
    
    if payloads.strip()=="":        
        with open(filename, "r") as f:
            result = [line.strip() for line in f if line.strip()]
            print(f"\nLoading payloads from file: {filename}\n")       
    else:        
        result=[line.strip() for line in payloads.strip().splitlines() if line.strip()]
        print(f"\nLoading payloads from inline list\n") 

    if debug!=0:
        print(result)
    return result

def _code_payloads(payloads_list, mode="", debug=0):    
    result = []
    if mode=="none":        
       result=payloads_list
    else:
        for payload in payloads_list:
            if mode == "url":
                # Standard URL encoding (space → %20)
                encoded = quote(payload)
            elif mode == "url+":
                # URL encoding like in Burp (space → +)
                encoded = quote_plus(payload)
            elif mode == "urlen":
                # application/x-www-form-urlencoded (key=value)
                # Using key "data" by default    
                encoded = urlencode({"data": payload})
            else:
                raise ValueError(f"Unknown encoding mode: {mode}")
            
            result.append(encoded)
    
    if debug != 0:
        print(result)
    return result


if __name__ == "__main__":
    main()
