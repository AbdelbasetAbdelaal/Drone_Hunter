"""Forwarder for target / enemy module."""
from src.entities.enemy import Enemy
from src.entities.boss import *
from src.systems.spawn_system import Spawner, WaveManager

Target = Enemy # Alias for compatibility
