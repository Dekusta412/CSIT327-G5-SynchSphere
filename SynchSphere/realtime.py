import time
import threading
from django.http import StreamingHttpResponse

# Very small in-memory pub/sub for simple SSE in development only.
_SUBSCRIBERS = []

def publish_event(event, data):
    payload = f"event: {event}\ndata: {data}\n\n"
    # copy to avoid mutation issues
    subs = list(_SUBSCRIBERS)
    for q in subs:
        q.append(payload)

class _Queue(list):
    pass

def event_stream(request):
    # Each client gets its own queue
    q = _Queue()
    _SUBSCRIBERS.append(q)

    def gen():
        try:
            # send a welcome event
            yield 'event: connected\ndata: connected\n\n'
            while True:
                if q:
                    item = q.pop(0)
                    yield item
                else:
                    time.sleep(0.2)
        finally:
            try:
                _SUBSCRIBERS.remove(q)
            except ValueError:
                pass

    return StreamingHttpResponse(gen(), content_type='text/event-stream')
