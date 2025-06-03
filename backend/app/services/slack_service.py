"""
Slack Service for DealTracker Sales Agent
Handles all Slack API interactions including sending messages, getting user info, etc.
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
import logging

logger = logging.getLogger(__name__)

class SlackService:
    """Service for interacting with Slack API"""
    
    def __init__(self):
        self.token = os.getenv("SLACK_BOT_TOKEN")
        self.channel_id = os.getenv("SLACK_CHANNEL_ID")
        self.client = None
        
        if self.token:
            self.client = AsyncWebClient(token=self.token)
        else:
            logger.warning("SLACK_BOT_TOKEN not found. Slack functionality will be disabled.")
    
    async def send_message(self, channel: str, text: str, blocks: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Send a message to a Slack channel"""
        if not self.client:
            logger.warning("Slack client not initialized. Message not sent.")
            return {"ok": False, "error": "slack_not_configured"}
        
        try:
            response = await self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks
            )
            return response.data
        except SlackApiError as e:
            logger.error(f"Error sending Slack message: {e.response['error']}")
            return {"ok": False, "error": e.response['error']}
        except Exception as e:
            logger.error(f"Unexpected error sending Slack message: {str(e)}")
            return {"ok": False, "error": str(e)}
    
    async def send_direct_message(self, user_id: str, text: str, blocks: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Send a direct message to a user"""
        if not self.client:
            logger.warning("Slack client not initialized. DM not sent.")
            return {"ok": False, "error": "slack_not_configured"}
        
        try:
            # Open a DM channel with the user
            dm_response = await self.client.conversations_open(users=[user_id])
            if not dm_response["ok"]:
                return {"ok": False, "error": "failed_to_open_dm"}
            
            channel_id = dm_response["channel"]["id"]
            
            # Send the message
            response = await self.client.chat_postMessage(
                channel=channel_id,
                text=text,
                blocks=blocks
            )
            return response.data
        except SlackApiError as e:
            logger.error(f"Error sending Slack DM: {e.response['error']}")
            return {"ok": False, "error": e.response['error']}
        except Exception as e:
            logger.error(f"Unexpected error sending Slack DM: {str(e)}")
            return {"ok": False, "error": str(e)}
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get information about a Slack user"""
        if not self.client:
            logger.warning("Slack client not initialized. Cannot get user info.")
            return {"ok": False, "error": "slack_not_configured"}
        
        try:
            response = await self.client.users_info(user=user_id)
            return response.data
        except SlackApiError as e:
            logger.error(f"Error getting user info: {e.response['error']}")
            return {"ok": False, "error": e.response['error']}
        except Exception as e:
            logger.error(f"Unexpected error getting user info: {str(e)}")
            return {"ok": False, "error": str(e)}
    
    async def get_channel_members(self, channel_id: str) -> List[str]:
        """Get list of members in a channel"""
        if not self.client:
            logger.warning("Slack client not initialized. Cannot get channel members.")
            return []
        
        try:
            response = await self.client.conversations_members(channel=channel_id)
            if response["ok"]:
                return response["members"]
            return []
        except SlackApiError as e:
            logger.error(f"Error getting channel members: {e.response['error']}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting channel members: {str(e)}")
            return []
    
    async def send_goal_prompt(self, user_id: str, user_name: str, prompt_text: str) -> Dict[str, Any]:
        """Send a goal-setting prompt to a user"""
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🎯 *Weekly Goal Setting - {user_name}*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": prompt_text
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Set Goals"
                        },
                        "style": "primary",
                        "action_id": "set_goals",
                        "value": user_id
                    }
                ]
            }
        ]
        
        return await self.send_direct_message(user_id, prompt_text, blocks)
    
    async def send_coaching_nudge(self, user_id: str, user_name: str, coaching_text: str) -> Dict[str, Any]:
        """Send a coaching nudge to a user"""
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"💡 *Coaching Tip - {user_name}*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": coaching_text
                }
            }
        ]
        
        return await self.send_direct_message(user_id, coaching_text, blocks)
    
    async def send_weekly_summary(self, user_id: str, user_name: str, summary_text: str) -> Dict[str, Any]:
        """Send a weekly summary to a user"""
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📊 *Weekly Summary - {user_name}*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": summary_text
                }
            }
        ]
        
        return await self.send_direct_message(user_id, summary_text, blocks)
    
    async def send_milestone_celebration(self, user_id: str, user_name: str, achievement: str) -> Dict[str, Any]:
        """Send a milestone celebration message"""
        celebration_text = f"🎉 Congratulations {user_name}! You've achieved: {achievement}"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🎉 *Achievement Unlocked - {user_name}*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": celebration_text
                }
            }
        ]
        
        # Send to both the user and the team channel
        dm_result = await self.send_direct_message(user_id, celebration_text, blocks)
        
        if self.channel_id:
            channel_result = await self.send_message(self.channel_id, celebration_text, blocks)
        else:
            channel_result = {"ok": True, "message": "No team channel configured"}
        
        return {
            "dm_sent": dm_result.get("ok", False),
            "channel_sent": channel_result.get("ok", False)
        }
    
    async def send_team_leaderboard(self, leaderboard_data: List[Dict]) -> Dict[str, Any]:
        """Send team leaderboard to the team channel"""
        if not self.channel_id:
            logger.warning("No team channel configured for leaderboard.")
            return {"ok": False, "error": "no_channel_configured"}
        
        # Format leaderboard text
        leaderboard_text = "🏆 *Weekly Sales Leaderboard*\n\n"
        
        for i, entry in enumerate(leaderboard_data[:10], 1):  # Top 10
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            name = entry.get("name", "Unknown")
            score = entry.get("score", 0)
            leaderboard_text += f"{emoji} {name}: {score} points\n"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": leaderboard_text
                }
            }
        ]
        
        return await self.send_message(self.channel_id, leaderboard_text, blocks)
    
    def is_configured(self) -> bool:
        """Check if Slack service is properly configured"""
        return self.client is not None and self.token is not None
    
    async def send_channel_message(self, channel_id: str, text: str, blocks: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Send a message to a specific channel (convenience method)"""
        return await self.send_message(channel_id, text, blocks)

# Global instance
slack_service = SlackService() 