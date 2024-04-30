import sounddevice as sd

from fastapi import FastAPI, Request
import uvicorn
import httpx
import numpy as np

port_controller = 7001
sound_device_name = "USB" # can be None for default device
block_size = 512
mock_server = "127.0.0.1:8765"

client = httpx.Client()
sound_bytes = np.zeros(block_size, dtype=np.float16)
app = FastAPI(docs_url="/")

@app.post("/sound_from_ai")
async def sound_from_ai(request: Request):
    global sound_bytes
    sound_bytes = np.frombuffer(await request.body(), dtype=np.float16)
    return "ok"

def callback(indata, outdata, frames, sdtime, status):
    # print("   received chunk of sound of length: ", indata.shape[0])
    outdata[:] = sound_bytes.reshape(frames, 1).astype(np.float32)
    input = indata[:,0].astype(np.float16)
    try:
        client.post(f"http://{mock_server}/sound_from_user", data=input.tobytes(), params={
            "user_ip": "55.22.33.44",
            "port_number": port_controller,
            "restaurant": "KFC"
            })
    except Exception as e:
        print("Error: ", e)

if __name__ == "__main__":    
    stream = sd.Stream(
        samplerate=48000,
        channels=1,
        callback=callback,
        blocksize=block_size,
        dtype=np.float32,
        device=sound_device_name,
        latency=0.01)
    with stream:
        uvicorn.run(app, host="0.0.0.0", port=port_controller)