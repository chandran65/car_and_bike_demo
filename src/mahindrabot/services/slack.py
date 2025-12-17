"""Slack notification service for sending messages to Slack channels via webhooks."""

import os
from typing import Optional

import requests


def send_message(message: str) -> None:
    """
    Send a message to Slack using a webhook URL.
    
    Args:
        message: The message text to send to Slack
        
    Raises:
        ValueError: If SLACK_WEBHOOK_URL environment variable is not set
        requests.exceptions.RequestException: If the request to Slack fails
    """
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    if not webhook_url:
        raise ValueError("SLACK_WEBHOOK_URL environment variable is not set")
    
    payload = {"text": message}
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(webhook_url, json=payload, headers=headers)
    response.raise_for_status()
