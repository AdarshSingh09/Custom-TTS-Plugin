import httpx
import soundfile as sf
import io
import numpy as np

# --- CONFIGURE YOUR SERVER'S IP ADDRESS HERE ---
EC2_SERVER_URL = "http://13.127.95.233:8000" # Replace with your EC2 Public IP

# This is the same data your agent sends
payload = {
  "input": "मैं स्कूल जाना चाहता हूँ",
  "voice": "hindi-159"
}

print("Attempting to connect to the API server...")

try:
    # Use httpx to make a request, just like the agent does
    with httpx.stream("POST", f"{EC2_SERVER_URL}/v1/audio/speech", json=payload, timeout=60.0) as response:
        print(f"Server responded with status code: {response.status_code}")
        response.raise_for_status() # This will raise an error if the status is not 2xx

        print("Receiving audio stream...")
        audio_bytes = response.read()

        # CORRECTED: Use a context manager to write the raw audio with the correct format
        with sf.SoundFile('test_output.wav', 'w', samplerate=24000, channels=1, subtype='PCM_16') as f:
            # The raw bytes need to be converted back to a numpy array to be written
            numpy_array = np.frombuffer(audio_bytes, dtype=np.int16)
            f.write(numpy_array)

        print("\nSuccess! Audio saved to 'test_output.wav'.")

except httpx.ConnectError as e:
    print("\n--- CONNECTION FAILED ---")
    print("Could not connect to the server. This is likely a firewall issue.")
    print(f"Error details: {e}")
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")