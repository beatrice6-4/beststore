from django.shortcuts import redirect

class WwwRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        if host.startswith('www.mamamaasaibakers.com'):
            # Redirect to non-www domain, preserving path and query
            new_url = 'https://mamamaasaibakers.com' + request.get_full_path()
            return redirect(new_url)
        return self.get_response(request)