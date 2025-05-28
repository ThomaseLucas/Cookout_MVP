from services.calendar_service import CalendarService
import logger
from supabase_setup import supabase
from datetime import datetime, timezone
import asyncio

class MealPlannerLogic():
    def __init__(self, bot):
        self.supabase_connection = supabase
        self.recipe_object = CalendarService()
        self.bot = bot
        

    def check_for_expired_date(self, data):
        if data['google_calendar_id'] == None:
            calendar_exists = self.recipe_object.check_if_calendar_exists(data['group'], data['name'] if data.get('name') else None)

            if calendar_exists:
                pass
            else:
                self.recipe_object.create_new_calendar(data['group'], data['name'] if data.get('name') else None)

        last_planned_at_str = data['last_planned_at']

        if last_planned_at_str:
            last_planned_at = datetime.fromisoformat(str(last_planned_at_str))
            now = datetime.now(timezone.utc)
            days_since_last_plan = (now - last_planned_at).days

        if data['last_planned_at'] == None or days_since_last_plan >= 7:
            return data['group']
        else:
            return None

    async def get_user_ids(self, group):
        group_users = supabase.table('users').select('discord_id').eq('group', group).execute()

        user_ids = [user['discord_id'] for user in group_users.data if user.get('discord_id')]
        return user_ids

    async def run_meal_plan_for_all_groups(self):
        groups_to_plan = []

        group_query = supabase.table('groups').select('*').execute()
        for data in group_query.data:
            result = self.check_for_expired_date(data)
            if result:
                groups_to_plan.append(result)
        lock = asyncio.Lock()
        group_plans = {}
        for group in groups_to_plan:
            if group not in group_plans:
                group_plans[group] = []
            
            group_plans[group] = await self.recipe_object.select_random_recipes(7, group, lock)

        group_user_ids = {}

        for group in group_plans:
            user_ids = await self.get_user_ids(group)
            group_user_ids[group] = user_ids
        
        for group, user_ids in group_user_ids.items():
            for user_id in user_ids:
                user = await self.bot.fetch_user(user_id)
                meal_plan_text = "\n".join([f"- {r['title']}" for r in group_plans[group]])
                await user.send(f"Your meal plan is here: {meal_plan_text}")

    


    

