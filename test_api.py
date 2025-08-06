import httpx
import soundfile as sf
import io
import numpy as np
import time

# --- CONFIGURE YOUR SERVER'S IP ADDRESS HERE ---
# Use the same URL as your agent.py file
EC2_SERVER_URL = "http://15.206.187.173:8000" 

# This is the same data your agent sends
# Set denoise and speed to their defaults to ensure streaming is enabled
payload = {
  "input": "मैं शाम तक नाचना चाहता हूँ",
  "voice": "hindi-43",
  "denoise": False,
  "speed": None,
}

print("Attempting to connect to the API server...")

try:
    # Use httpx to make a request, just like the agent does
    with httpx.stream("POST", f"{EC2_SERVER_URL}/v1/audio/speech", json=payload, timeout=60.0) as response:
        print(f"Server responded with status code: {response.status_code}")
        response.raise_for_status() # This will raise an error if the status is not 2xx

        print("Receiving audio stream chunk by chunk...")
        
        audio_chunks = []
        start_time = time.time()
        first_byte_time = None

        # Iterate over the bytes as they are received from the server
        for chunk in response.iter_bytes():
            if first_byte_time is None:
                first_byte_time = time.time()
                ttfb = (first_byte_time - start_time) * 1000  # Time to First Byte in ms
                print(f"First chunk received in: {ttfb:.2f} ms")

            audio_chunks.append(chunk)

        # After the loop finishes, combine all chunks into one byte string
        audio_bytes = b"".join(audio_chunks)
        
        if not audio_bytes:
            print("\n--- ERROR ---")
            print("No audio data was received from the server.")
        else:
            # The raw bytes need to be converted back to a numpy array to be written
            numpy_array = np.frombuffer(audio_bytes, dtype=np.int16)
            
            # Use a context manager to write the raw audio with the correct format
            sf.write('test_output.wav', numpy_array, samplerate=24000, subtype='PCM_16')

            print("\nSuccess! Audio saved to 'test_output.wav'.")

except httpx.ConnectError as e:
    print("\n--- CONNECTION FAILED ---")
    print("Could not connect to the server. Check the IP address and ensure the server is running.")
    print(f"Error details: {e}")
except httpx.HTTPStatusError as e:
    print(f"\n--- HTTP ERROR ---")
    print(f"Server returned a non-200 status code: {e.response.status_code}")
    print(f"Response body: {e.response.text}")
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")
