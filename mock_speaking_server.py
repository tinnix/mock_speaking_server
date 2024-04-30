from fastapi import FastAPI, Request
import uvicorn
import numpy as np
import httpx
import time
import soundfile as sf
import threading
import queue

server_port = 8765

# read the test.wav file as numpy array
test_sound = sf.read("test.wav")[0].astype(np.float16)
upsample = 48000 // 16000
test_sound = np.repeat(test_sound, upsample, axis=0)

all_clients = {}
processing_queue = queue.Queue()
client = httpx.Client()

app = FastAPI(docs_url="/")

@app.post("/sound_from_user")
async def sound_from_user(user_ip: str, port_number: int, restaurant: str, request: Request):
    global all_clients, processing_queue
    client_key = user_ip + ":" + str(port_number)
    if client_key not in all_clients:
        print("New client: ", client_key)
        all_clients[client_key] = {
                "sent_samples": 0
            }
        
    sound_bytes = np.frombuffer(await request.body(), dtype=np.float16)
    print("   received chunk of sound of length: ", sound_bytes.shape[-1])
    processing_queue.put({
                "user_ip": user_ip,
                "sending_ip": request.client.host,
                "port_number": port_number,
                "restaurant": restaurant,
                "in_sound": sound_bytes,
            })
    return "ok"

def mock_client_processor():
    global all_clients, processing_queue
    while(True):
        item = processing_queue.get()
        processing_queue.task_done()
        client_key = item["user_ip"] + ":" + str(item["port_number"])
        sound = item["in_sound"]
        # add part of test_sound starting from sent_samples
        test_sound_start_index = all_clients[client_key]["sent_samples"]
        if test_sound_start_index + sound.shape[-1] > test_sound.shape[-1]:
            test_sound_start_index = 0
        sound = sound + test_sound[test_sound_start_index:test_sound_start_index+sound.shape[-1]]
        all_clients[client_key]["sent_samples"] = test_sound_start_index + sound.shape[-1]
        server = f"http://{item['sending_ip']}:{item['port_number']}/sound_from_ai"
        print("\n\n   sending chunk to: ", server, " of length: ", sound.shape[-1])
        try:
            client.post(server, data=sound.tobytes())
        except Exception as e:
            print("Error: ", e)

if __name__ == "__main__":
    threading.Thread(target=mock_client_processor).start()
    uvicorn.run(app, host="0.0.0.0", port=server_port)
    