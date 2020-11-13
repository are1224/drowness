from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import drowsiness.routing

application = ProtocolTypeRouter({
    #(http->django views is added by default)
    'websocket' : AuthMiddlewareStack(
        URLRouter(
            drowsiness.routing.websocket_urlpatterns
        )
    ) 
})