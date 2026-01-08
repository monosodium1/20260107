from flask import Response
import json
import time

def generate_sse_response(data_generator):
    def generate():
        try:
            for data in data_generator:
                yield f"data: {json.dumps(data)}\n\n"
        except GeneratorExit:
            pass
    return Response(generate(), mimetype='text/event-stream')

def broadcast_message(socketio, event, data, room=None):
    if room:
        socketio.emit(event, data, room=room)
    else:
        socketio.emit(event, data, broadcast=True)
