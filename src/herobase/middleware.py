# -*- coding: utf-8 -*-


class IsMobileMiddleware(object):
    def process_request(self, request):
        path = request.META['PATH_INFO']
        request.is_mobile = path == '/m' or path.startswith('/m/')