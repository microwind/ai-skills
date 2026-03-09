#!/usr/bin/env python3
import sys
import json
from urllib.parse import urljoin
import time

def test_api_endpoint(url, method='GET', headers=None, body=None):
    '''Test API endpoint and return detailed results'''
    result = {
        'url': url,
        'method': method,
        'status': None,
        'time_ms': 0,
        'response': None,
        'error': None,
        'headers': {},
        'tests': []
    }

    try:
        import urllib.request
        import urllib.error

        # Prepare request
        req = urllib.request.Request(url, method=method)
        if headers:
            for k, v in headers.items():
                req.add_header(k, v)

        if body:
            if isinstance(body, dict):
                body = json.dumps(body)
            req.data = body.encode() if isinstance(body, str) else body

        # Make request
        start = time.time()
        try:
            with urllib.request.urlopen(req) as response:
                elapsed = (time.time() - start) * 1000
                result['time_ms'] = int(elapsed)
                result['status'] = response.status
                result['headers'] = dict(response.headers)

                content = response.read().decode()
                result['response'] = content

                # Try to parse as JSON
                try:
                    result['response'] = json.loads(content)
                except:
                    pass

                # Run basic tests
                result['tests'].append({
                    'name': 'Status code',
                    'passed': response.status < 400,
                    'status': response.status
                })

                result['tests'].append({
                    'name': 'Response time',
                    'passed': result['time_ms'] < 5000,
                    'time_ms': result['time_ms']
                })

        except urllib.error.HTTPError as e:
            result['status'] = e.code
            result['error'] = f'HTTP {e.code}: {e.reason}'

    except Exception as e:
        result['error'] = f'Error: {str(e)}'

    return result

if __name__ == '__main__':
    # Example: python test_api.py GET https://api.example.com/users
    if len(sys.argv) < 3:
        print('Usage: test_api.py METHOD URL [HEADERS] [BODY]')
        sys.exit(1)

    method = sys.argv[1]
    url = sys.argv[2]
    headers = {'User-Agent': 'API-Tester/1.0'}

    result = test_api_endpoint(url, method=method, headers=headers)
    print(json.dumps(result, indent=2, default=str))
