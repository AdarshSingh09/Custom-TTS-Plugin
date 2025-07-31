# 🗣️ Custom TTS Plugin

This project contains a **custom Text-to-Speech (TTS) plugin** for livekit which connects to a api running on an EC2 instance, along with scripts to test the API and run a local voice agent.

---

## 🖥️ Step-by-Step: Start and Run the EC2 TTS Server

### 1. Start the EC2 Instance

Start the EC2 instance named: `tts-ec2-server`

### 2. Copy the Public IP Address

Once the instance is running, copy its **public IPv4 address** from the AWS console.

---

### 3. SSH into the EC2 Instance

Use the following command, replacing `<your-ec2-ip-address>` with the actual IP:

```bash
ssh -i tts-key.pem ubuntu@<your-ec2-ip-address>
```

### 4. Activate the Virtual Environment

Once logged in, activate the Python virtual environment:

```bash
source snor_tts_venv/bin/activate
```

### 5. Run the TTS Server

Start the server by running:
```bash
python tts_server.py
```
Your EC2 TTS server should now be running and listening on port 8000.

## 🔬 Testing the TTS API

### 1. Update EC2 Server URL in test_api.py 

Open test_api.py and modify the ```EC2_SERVER_URL```

### 2. Run the Test Script 

```bash
python test_api.py
```

### 3. Output 

The script will generate a .wav audio file as output

## 🧠 Running the Local Voice Agent
### - Modify the ```EC2_SERVER_URL``` in agent.py
### - Run the Agent Locally using: 
```bash 
python agent.py console
```
