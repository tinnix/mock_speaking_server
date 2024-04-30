# Mock speaking server for testing the WebRTC sound connections

## 1. Installation
Clone git repo and install requirements:
```
git clone https://github.com/hidoba/mock_speaking_server
cd mock_speaking_server
pip install -r requirements.txt
```

## 2. Running
```
python mock_speaking_server.py
```
will create a mock server listening on port `8765`.

The server has a POST method `/sound_from_user` that has sound data as it's body in float16 format, and the following parameters:
- user_ip : remote user ip for identification, will not be used
- port_number: port number that the server will send data to
- restaurant: string corresponding to the restaurant

The server will send sound data back to where the response originated from, using the POST method `/sound_from_ai` with the raw sound data in the body in float16 format.

## 3. The rest

`sound_test.py` is just for testing the `mock_speaking_server.py`, it's not needed for running the server and can be ignored.