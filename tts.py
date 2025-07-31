# tts.py - A custom TTS plugin for our Indic TTS API
# This version is corrected to match the official LiveKit plugin structure.

from __future__ import annotations
from dataclasses import dataclass
import httpx
import asyncio

# LiveKit Agents imports
from livekit.agents import (
    tts,
    utils,
    APIConnectOptions,
    DEFAULT_API_CONNECT_OPTIONS,
    APIConnectionError,
    APITimeoutError,
    APIStatusError,
)
from livekit.rtc import AudioFrame

# ==============================================================================
# This dataclass holds the specific options for our TTS plugin.
# ==============================================================================
@dataclass
class _TTSOptions:
    voice: str
    denoise: bool

# ==============================================================================
# This is the main plugin class that the LiveKit agent will interact with.
# ==============================================================================
class TTS(tts.TTS):
    def __init__(
        self,
        *,
        voice: str = "hindi-159",
        denoise: bool = True,
        base_url: str,
    ):
        super().__init__(
            capabilities=tts.TTSCapabilities(streaming=False),  # Correctly set to False
            sample_rate=24000,
            num_channels=1,
        )
        self._client = httpx.AsyncClient(timeout=60.0)
        self._base_url = base_url
        self._opts = _TTSOptions(voice=voice, denoise=denoise)

    def synthesize(self, text: str, *, conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS) -> "ChunkedStream":
        """
        This is the primary method called by the LiveKit agent.
        It creates and returns a stream object that will handle the synthesis.
        """
        return ChunkedStream(
            tts=self,
            input_text=text,
            conn_options=conn_options,
        )

# ==============================================================================
# This class handles the actual API call and streaming of audio data.
# It now correctly inherits from ChunkedStream.
# ==============================================================================
class ChunkedStream(tts.ChunkedStream):
    def __init__(
        self,
        *,
        tts: TTS,
        input_text: str,
        conn_options: APIConnectOptions,
    ):
        super().__init__(tts=tts, input_text=input_text, conn_options=conn_options)
        self._tts: TTS = tts

    async def _run(self, output_emitter: tts.AudioEmitter) -> None:
        """
        The core logic that connects to our API and streams the audio,
        using the correct AudioEmitter pattern.
        """
        try:
            # Initialize the output emitter with all required parameters
            output_emitter.initialize(
                request_id=utils.shortuuid(),
                sample_rate=self._tts.sample_rate,
                num_channels=self._tts.num_channels,
                mime_type="audio/raw",  # Match our FastAPI server's output
            )

            payload = {
                "input": self.input_text,
                "voice": self._tts._opts.voice,
                "denoise": self._tts._opts.denoise,
            }

            async with self._tts._client.stream(
                "POST",
                f"{self._tts._base_url}/v1/audio/speech",
                json=payload,
            ) as response:
                
                response.raise_for_status()

                # Push raw bytes directly to the emitter
                async for chunk in response.aiter_bytes():
                    output_emitter.push(chunk)
            
            # Only flush the emitter after a successful synthesis
            output_emitter.flush()

        except httpx.TimeoutException as e:
            raise APITimeoutError() from e
        except httpx.HTTPStatusError as e:
            raise APIStatusError(
                f"Server returned an error: {e.response.status_code}",
                status_code=e.response.status_code,
            ) from e
        except Exception as e:
            raise APIConnectionError() from e
