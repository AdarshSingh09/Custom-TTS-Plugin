# agent.py - A full conversational agent using the modern agent architecture

import os
from dotenv import load_dotenv

# LiveKit Agents imports
from livekit import agents
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import silero, google, sarvam

# Import our custom TTS class from the tts.py file
from tts import TTS

# Load environment variables from a .env file
load_dotenv()

# ==============================================================================
# 1. THE CONVERSATIONAL AGENT LOGIC
# ==============================================================================

class MyAssistant(Agent):
    def __init__(self) -> None:
        # --- CONFIGURE YOUR SERVER'S IP ADDRESS HERE ---
        EC2_SERVER_URL = "http://13.127.95.233:8000" # Replace with your EC2 Public IP

        # Create an instance of our custom TTS plugin
        custom_tts = TTS(
            base_url=EC2_SERVER_URL,
            voice="hindi-159",  # Matches your FastAPI format
            denoise=True
        )

        super().__init__(
            stt=sarvam.STT(
                language="hi-IN",
                model="saarika:v2.5",
            ),
            vad=silero.VAD.load(),
            llm=google.LLM(model="gemini-1.5-flash"),
            tts=custom_tts,
            instructions="You are a helpful and friendly voice assistant. Your goal is to assist users with their questions. Keep your responses concise and conversational.",
        )

    async def on_enter(self):
        """
        A callback that is executed when the agent first joins the room.
        Used here to greet the user.
        """
        await self.session.say("नमस्ते! मैं आपकी कैसे सहायता कर सकता हूं?")

async def entrypoint(ctx: JobContext):
    """
    This is the main entrypoint for the agent worker. It creates the
    AgentSession and starts it with our custom agent.
    """
    print("Starting conversational agent entrypoint...")
    session = AgentSession()
    await session.start(
        agent=MyAssistant(),
        room=ctx.room
    )

# ==============================================================================
# 2. AGENT EXECUTION
# ==============================================================================

if __name__ == "__main__":
    # To run this agent:
    # 1. Make sure your EC2 server is running the main.py API.
    # 2. Make sure the tts.py file is in the same directory as this agent.py file.
    # 3. Install all the necessary dependencies in your local venv:
    #    pip install "livekit-agents[google]~=1.0" livekit-plugins-sarvam livekit-plugins-silero python-dotenv httpx openai
    # 4. Create a .env file in this directory with your API keys:
    #    SARVAM_API_KEY="your_sarvam_key"
    #    GOOGLE_API_KEY="your_google_ai_studio_key"
    # 5. Run this script from your terminal with a command:
    #    python agent.py console  (to talk to it in your terminal)
    
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
