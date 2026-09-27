"""Colab Bridge: Remote Worker Integration for Video Pilot.

Provides automated offloading of heavy computational tasks (Remotion Video
Rendering, High-VRAM Expressive TTS, AI Post-processing) to Google Colab GPU.
"""

from .config import ColabConfig, get_colab_config
from .client import ColabClient, is_colab_available

__all__ = [
    'ColabConfig',
    'get_colab_config',
    'ColabClient',
    'is_colab_available',
]
