# agent.py - A full conversational agent using the modern agent architecture

import os
from dotenv import load_dotenv

# LiveKit Agents imports
from livekit import agents
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import silero, google, deepgram, sarvam
from livekit.agents import metrics  
from livekit.agents.voice import MetricsCollectedEvent

# Import our custom TTS class from the tts.py file
from tts import TTS

load_dotenv()

# ==============================================================================
# 1. THE CONVERSATIONAL AGENT LOGIC
# ==============================================================================

class MyAssistant(Agent):
    def __init__(self) -> None:
        # --- CONFIGURE YOUR SERVER'S IP ADDRESS HERE ---
        EC2_SERVER_URL = "https://audio.dubverse.ai/api" # Replace with your EC2 Public IP

        # Create an instance of our custom TTS plugin
        custom_tts = TTS(
            api_key="rdlNCp9H7tma9hMRvvF77k29VLEYpgbu",
            voice="200",
            base_url=EC2_SERVER_URL,
        )

        super().__init__(
            stt=sarvam.STT(language="kn-IN", model="saarika:v2.5"),
            vad=silero.VAD.load(),
            llm=google.LLM(model="gemini-2.5-flash"),
            tts=custom_tts,
            instructions="ನೀನು ಸಹಾಯಕ ಹಾಗೂ ಸ್ನೇಹಪೂರ್ಣ ಧ್ವನಿ ಸಹಾಯಕನು. ಬಳಕೆದಾರರು ಕೇಳುವ ಪ್ರಶ್ನೆಗಳಿಗೆ ಸಹಾಯ ಮಾಡುವುದೇ ನಿನ್ನ ಉದ್ದೇಶ. ನಿನ್ನ ಉತ್ತರಗಳು ಸರಳವಾಗಿದ್ದು, ಮಾತಿನಶೈಲಿಯಲ್ಲಿ ಇರಲಿ.",
        )

    async def on_enter(self):
        """
        A callback that is executed when the agent first joins the room.
        Used here to greet the user.
        """
        await self.session.say("ನಮಸ್ಕಾರ! ನಾನು ಇಂದು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?")

async def entrypoint(ctx: JobContext):
    """
    This is the main entrypoint for the agent worker. It creates the
    AgentSession and starts it with our custom agent.
    """
    print("Starting conversational agent entrypoint...")
    session = AgentSession()

    # Create usage collector for metrics  
    usage_collector = metrics.UsageCollector()  
    
    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):    
        metrics.log_metrics(ev.metrics)    
        usage_collector.collect(ev.metrics)
    
    await session.start(
        agent=MyAssistant(),
        room=ctx.room
    )

# ==============================================================================
# 2. AGENT EXECUTION
# ==============================================================================

if __name__ == "__main__":
    
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
