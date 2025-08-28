from dataclasses import dataclass, field
from typing import Dict, Optional
from urllib.parse import quote, quote_plus, urlencode
import re
import httpx
import time

# === Colors ===
RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"

@dataclass
class HTTPRequest:
    method: str
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    data: Optional[str] = None
    http_version: str = "HTTP/1.1"

    def __str__(self):
        lines = [f"{self.method} {self.url} {self.http_version}"]
        for k, v in self.headers.items():
            lines.append(f"{k}: {v}")
        if self.cookies:
            cookie_str = "; ".join([f"{k}={v}" for k, v in self.cookies.items()])
            lines.append(f"Cookie: {cookie_str}")
        lines.append("")
        if self.data:
            lines.append(self.data)
        return "\n".join(lines)

def _get_method(request: str) -> str:
    return request.strip().splitlines()[0].split()[0].upper()

def _get_http_version(request: str) -> str:
    return request.strip().splitlines()[0].split()[-1].upper()

def _get_url(request: str) -> str:
    return request.strip().splitlines()[0].split()[1]

def _get_headers(request: str) -> Dict[str, str]:    
    lines = request.strip().splitlines()
    headers = {}
    for line in lines[1:]:
        if not line.strip() or line.lower().startswith("cookie:"):
            continue
        if ": " in line:
            key, value = line.split(": ", 1)
            headers[key.strip()] = value.strip()
    return headers

def _get_cookies(request: str) -> Dict[str, str]:
    for line in request.strip().splitlines():
        if line.lower().startswith("cookie:"):
            cookie_str = line[len("cookie:"):].strip()
            return dict(item.split("=", 1) for item in cookie_str.split("; ") if "=" in item)
    return {}

def _get_data(request: str) -> Optional[str]:
    parts = request.strip().split("\n\n", 1)
    if len(parts) == 2:
        return parts[1].strip()
    return None

def _load_payloads(payloads, filename, debug=0):
    if payloads.strip() == "":
        with open(filename, "r") as f:
            result = [line.strip() for line in f if line.strip()]
        print(f"[INFO] Payloads loaded from file: {filename} ({len(result)} payloads)")
    else:
        result = [line.strip() for line in payloads.strip().splitlines() if line.strip()]
        print(f"[INFO] Payloads loaded from inline list ({len(result)} payloads)")

    if debug:
        print("[DEBUG] Payload list:")
        print(result)
    return result

def _payloads_codes(payloads_baypas, mode="", debug=0):   
    result = []
    if mode == "none":        
        result = payloads_baypas
    else:
        for payload in payloads_baypas:
            if mode == "url":
                encoded = quote(payload)
            elif mode == "url+":
                encoded = quote_plus(payload)
            elif mode == "urlen":
                encoded = urlencode({"data": payload})
            else:
                raise ValueError(f"Unknown encoding mode: {mode}")
            result.append(encoded)

    if debug:
        print("[DEBUG] Encoded payloads:")
        print(result)
    return result

def _list_request(raw_request, debug=0):
    result = []
    positions = [m.start() for m in re.finditer("FUZZ", raw_request)]

    if not positions:
        print("[INFO] No FUZZ markers found. Using original request.")
        return [raw_request], "", ""

    print(f"[INFO] FUZZ markers found: {len(positions)}")

    for i, pos in enumerate(positions):
        temp = raw_request[:pos] + "{{PAYLOAD}}" + raw_request[pos + len("FUZZ"):]
        temp = temp.replace("FUZZ", "")
        result.append(temp)

    if debug:
        for i, r in enumerate(result):
            print(f"\n[DEBUG] Template #{i+1}:\n{r}")
    return result

def _list_request_and_payloads(payloads, request, debug=0):
    result = []
    for template in request:
        for payload in payloads:
            modified = [line.replace("{{PAYLOAD}}", payload) for line in template.splitlines()]
            result.append(modified)
            if debug:
                print("\n".join(modified))
                print("-" * 50)
    print(f"[INFO] Total requests generated: {len(result)}")
    return result

def prepare_requests(requests,debug=0):
    result = []
    for i, request_lines in enumerate(requests, 0):
        request = "\n".join(request_lines)
        example = HTTPRequest(
            method=_get_method(request),
            http_version=_get_http_version(request),
            url=_get_url(request),
            headers=_get_headers(request),
            cookies=_get_cookies(request),
            data=_get_data(request)
        )
        result.append(example)
        if debug:
            print(example)
    return result

def _ideal_request(raw_request, debug=0):
    cleaned = raw_request.replace("FUZZ", "")
    result = [cleaned.splitlines()]
    if debug:
        print("\n[DEBUG] Cleaned request (no FUZZ):")
        print("\n".join(result[0]))
    return result

def send_request(req, scheme, timeout=10, debug=0):
    http2 = True if req.http_version == "HTTP/2" else False

    start = time.perf_counter()
    try:
        with httpx.Client(http2=http2, cookies=req.cookies, timeout=timeout) as client:
            response = client.request(
                method=req.method,            
                url = f"{scheme}://{req.headers['Host']}{req.url}",
                headers=req.headers,
                data=req.data
            )
        elapsed = time.perf_counter() - start
        return response, elapsed
    except httpx.ReadTimeout:
        elapsed = time.perf_counter() - start
        return None, elapsed

def print_result(label, response, elapsed, baseline_time, ideal_length):
    if response is None:
        print(f"{RED}[TIMEOUT] > {baseline_time}s (actual {elapsed:.2f}s){RESET}")
        return

    status = response.status_code
    length = len(response.text)

    msg = f"[{label}] Status: {status} | Length: {length} | Time: {elapsed:.2f}s"

    # глобальные отличия
    if abs(elapsed - baseline_time) < 0.5:
        print(f"{GREEN}{msg}  <-- time-based candidate{RESET}")
    elif status != 200 or length != ideal_length:
        print(f"{GREEN}{msg}  <-- anomaly{RESET}")
    else:
        print(msg)

def send_all_requests(prepared_requests, scheme, baseline_time, ideal_length):
    for i, req in enumerate(prepared_requests, 1):
        response, elapsed = send_request(req, scheme)
        print_result(f"REQ#{i}", response, elapsed, baseline_time, ideal_length)

# === Settings ===
filename = "payloads.txt"
payloads = """
"""
raw = """GET /FUZZ HTTP/1.1
Host: 127.0.0.1
Cookie: session=XYBkJt64Sgg1MKF26DPTzlCOkKGOTX2FFUZZ
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
scheme = "http"  # or "https"
baseline_time = 5  # эталон для time-based SQLi

def main():
    payloads_load = _load_payloads(payloads, filename, debug=0)
    payloads_baypas = payloads_load
    payloads_codes = _payloads_codes(payloads_baypas, "none", debug=0)

    request_list = _list_request(raw, debug=0)
    final_requests = _list_request_and_payloads(payloads_codes, request_list, debug=0)    
    prepared_requests = prepare_requests(final_requests,debug=0)
    print(f"[INFO] Final request objects to be processed: {len(final_requests)}")

    ideal_request=_ideal_request(raw,debug=0)
    prepared_ideal_requests = prepare_requests(ideal_request,debug=0)

    # эталон
    response, elapsed = send_request(prepared_ideal_requests[0], scheme)
    ideal_length = len(response.text) if response else 0
    print_result("IDEAL", response, elapsed, baseline_time, ideal_length)

    # все с payload'ами
    send_all_requests(prepared_requests, scheme, baseline_time, ideal_length)

if __name__ == "__main__":
    main()
