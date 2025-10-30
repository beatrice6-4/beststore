from django.shortcuts import redirect

class WwwRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        # Strictly redirect any www.mamamaasaibakers.com to mamamaasaibakers.com
        if host.lower().startswith('www.mamamaasaibakers.com'):
            new_url = 'https://mamamaasaibakers.com' + request.get_full_path()
            # Permanent redirect (HTTP 301)
            return redirect(new_url, permanent=True)
        return self.get_response(request)