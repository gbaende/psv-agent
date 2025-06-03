"""
AI Service for DealTracker Sales Agent
Handles all AI-powered content generation using OpenAI API
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered content generation"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        
        if self.api_key:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=self.api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}. AI functionality will be disabled.")
                self.client = None
        else:
            logger.warning("OPENAI_API_KEY not found. AI functionality will be disabled.")
    
    async def generate_weekly_goal_prompt(self, user_name: str, previous_performance: Dict = None) -> str:
        """Generate a personalized weekly goal-setting prompt"""
        if not self.client:
            return self._get_fallback_goal_prompt(user_name)
        
        try:
            # Build context based on previous performance
            context = f"Generate a motivational weekly goal-setting prompt for {user_name}, a sales representative."
            
            if previous_performance:
                context += f"\nPrevious week performance: {previous_performance}"
            
            context += "\nThe prompt should be encouraging, specific, and help them set realistic but challenging goals for the upcoming week."
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are SalesPM, an AI sales project manager. Generate encouraging and personalized goal-setting prompts."},
                    {"role": "user", "content": context}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating goal prompt: {str(e)}")
            return self._get_fallback_goal_prompt(user_name)
    
    async def generate_coaching_tip(self, user_name: str, performance_data: Dict = None) -> str:
        """Generate a personalized coaching tip"""
        if not self.client:
            return self._get_fallback_coaching_tip(user_name)
        
        try:
            context = f"Generate a helpful coaching tip for {user_name}, a sales representative."
            
            if performance_data:
                context += f"\nCurrent performance data: {performance_data}"
            
            context += "\nThe tip should be actionable, encouraging, and help improve their sales performance."
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are SalesPM, an AI sales coach. Provide practical and encouraging coaching tips."},
                    {"role": "user", "content": context}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating coaching tip: {str(e)}")
            return self._get_fallback_coaching_tip(user_name)
    
    async def generate_weekly_summary(self, user_name: str, week_data: Dict) -> str:
        """Generate a personalized weekly performance summary"""
        if not self.client:
            return self._get_fallback_weekly_summary(user_name, week_data)
        
        try:
            context = f"Generate a weekly performance summary for {user_name}.\n"
            context += f"Week data: {week_data}\n"
            context += "Include achievements, areas for improvement, and encouragement for next week."
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are SalesPM, an AI sales manager. Create comprehensive but encouraging weekly summaries."},
                    {"role": "user", "content": context}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating weekly summary: {str(e)}")
            return self._get_fallback_weekly_summary(user_name, week_data)
    
    async def analyze_goals(self, goals_text: str) -> Dict[str, Any]:
        """Analyze and parse goals from user input"""
        if not self.client:
            return self._get_fallback_goal_analysis(goals_text)
        
        try:
            context = f"Analyze the following sales goals and extract structured data:\n{goals_text}\n"
            context += "Return a JSON object with: calls_goal, meetings_goal, revenue_goal, and any other specific goals mentioned."
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant that extracts structured goal data from text. Always respond with valid JSON."},
                    {"role": "user", "content": context}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            # Try to parse the JSON response
            import json
            try:
                return json.loads(response.choices[0].message.content.strip())
            except json.JSONDecodeError:
                return self._get_fallback_goal_analysis(goals_text)
            
        except Exception as e:
            logger.error(f"Error analyzing goals: {str(e)}")
            return self._get_fallback_goal_analysis(goals_text)
    
    async def generate_milestone_celebration(self, user_name: str, achievement: str) -> str:
        """Generate a celebration message for achievements"""
        if not self.client:
            return f"🎉 Congratulations {user_name}! You've achieved: {achievement}. Keep up the great work!"
        
        try:
            context = f"Generate an enthusiastic celebration message for {user_name} who achieved: {achievement}"
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are SalesPM, an enthusiastic AI sales manager. Create celebratory messages for achievements."},
                    {"role": "user", "content": context}
                ],
                max_tokens=150,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating celebration: {str(e)}")
            return f"🎉 Congratulations {user_name}! You've achieved: {achievement}. Keep up the great work!"
    
    async def generate_response(self, prompt: str, system_message: str = None) -> str:
        """Generate a general AI response for any prompt"""
        if not self.client:
            return "AI functionality is currently unavailable. Please check your OpenAI API configuration."
        
        try:
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            else:
                messages.append({"role": "system", "content": "You are SalesPM, an AI sales project manager assistant."})
            
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return f"I apologize, but I'm having trouble generating a response right now. Error: {str(e)}"
    
    def _get_fallback_goal_prompt(self, user_name: str) -> str:
        """Fallback goal prompt when AI is not available"""
        return f"""🎯 Good morning {user_name}!

It's time to set your goals for this week. Let's make it a great one!

Please share your goals for:
• Number of calls you plan to make
• Meetings you want to schedule
• Revenue target you're aiming for
• Any specific prospects you want to focus on

Remember, the best goals are specific, measurable, and achievable. What are you going to accomplish this week?"""
    
    def _get_fallback_coaching_tip(self, user_name: str) -> str:
        """Fallback coaching tip when AI is not available"""
        tips = [
            f"💡 {user_name}, remember that every 'no' gets you closer to a 'yes'. Keep pushing forward!",
            f"🎯 {user_name}, focus on building relationships, not just closing deals. Trust leads to sales.",
            f"📞 {user_name}, try to make your first call of the day to your most challenging prospect. Start strong!",
            f"✨ {user_name}, listen more than you speak. Your prospects will tell you exactly how to sell to them.",
            f"🚀 {user_name}, celebrate small wins! They build momentum for bigger victories."
        ]
        import random
        return random.choice(tips)
    
    def _get_fallback_weekly_summary(self, user_name: str, week_data: Dict) -> str:
        """Fallback weekly summary when AI is not available"""
        return f"""📊 Weekly Summary for {user_name}

This week's highlights:
• Goals set and progress tracked
• Continued focus on sales activities
• Building momentum for next week

Keep up the great work! Every week is a new opportunity to excel. 🚀"""
    
    def _get_fallback_goal_analysis(self, goals_text: str) -> Dict[str, Any]:
        """Fallback goal analysis when AI is not available"""
        # Simple keyword-based extraction
        import re
        
        analysis = {
            "calls_goal": 0,
            "meetings_goal": 0,
            "revenue_goal": 0,
            "other_goals": []
        }
        
        # Look for numbers followed by common keywords
        calls_match = re.search(r'(\d+).*(?:call|dial)', goals_text.lower())
        if calls_match:
            analysis["calls_goal"] = int(calls_match.group(1))
        
        meetings_match = re.search(r'(\d+).*(?:meeting|appointment)', goals_text.lower())
        if meetings_match:
            analysis["meetings_goal"] = int(meetings_match.group(1))
        
        revenue_match = re.search(r'[\$]?(\d+(?:,\d{3})*(?:\.\d{2})?)', goals_text)
        if revenue_match:
            analysis["revenue_goal"] = float(revenue_match.group(1).replace(',', ''))
        
        return analysis
    
    def is_configured(self) -> bool:
        """Check if AI service is properly configured"""
        return self.client is not None and self.api_key is not None

# Global instance - initialize safely
try:
    ai_service = AIService()
except Exception as e:
    logger.error(f"Failed to initialize AI service: {e}")
    # Create a fallback instance
    ai_service = AIService()
    ai_service.client = None 