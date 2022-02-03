from headers import *
from config import *
from get import *

class Head:

    def HEAD(self, request):
        head = Get()
        response, pnp, exception = head.GET(request, '', 'HEAD')
        
        return response, pnp, exception
