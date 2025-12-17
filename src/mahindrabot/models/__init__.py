"""Pydantic models for car data structures."""

from .ev_location import Coordinates, EVLocationResult

__all__ = [
    "EVLocationResult",
    "Coordinates",
]
