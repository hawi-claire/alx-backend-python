#!/usr/bin/env python3
"""Async Comprehension module"""
from typing import List

async_generator = __import__('0-async_generator').async_generator


async def async_comprehension() -> List[float]:
    """
    Coroutine that collects 10 random numbers using an async comprehension.
    
    Returns:
        List[float]: 10 random float numbers collected from async_generator
    """
    return [number async for number in async_generator()]
