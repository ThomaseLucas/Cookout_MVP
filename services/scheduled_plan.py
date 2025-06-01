from services.calendar_service import CalendarService
import logger
from supabase_setup import supabase
from datetime import datetime, timezone
import asyncio
from services.reroll import RerollButtonView
from services.newlistbutton import NewListView
from services.confirmbutton import ConfirmButtonView
import discord

class MealPlanner():
    def __init__(self, bot):
        self.supabase_connection = supabase
        self.calendar_object = CalendarService()
        self.bot = bot
        

    def check_for_expired_date(self, data):
        if data['google_calendar_id'] == None:
            calendar_exists = self.calendar_object.check_if_calendar_exists(data['group'], data['name'] if data.get('name') else None)

            if calendar_exists:
                pass
            else:
                self.calendar_object.create_new_calendar(data['group'], data['name'] if data.get('name') else None)

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

    def confirm_clicked(self):
        pass 

    async def run_meal_plan_for_all_groups(self, group=None):
        if not group:
            groups_to_plan = []

            group_query = supabase.table('groups').select('*').execute() #This query gets the group numbers which haven't had a meal plan made in 7 days. 
            for data in group_query.data:
                result = self.check_for_expired_date(data) 
                if result:
                    groups_to_plan.append(result) #creates a list of all the groups that we need a meal plan for
                    
            lock = asyncio.Lock()
            group_plans = {} #This dictionary is here to store the meal plan for each group. Structure: group_plans[1] = [{'title': 'Pizza'}, {'ingredients': 'Cheese'}]
            for group in groups_to_plan:
                if group not in group_plans:
                    group_plans[group] = [] 
                
                group_plans[group] = await self.calendar_object.select_random_recipes(7, group, lock) #creates a list of objects that holds the title and id of the recipe for later calling to be able to show the user, and fill out a calendar.
        else:
            lock = asyncio.Lock()
            group_plans[group] = await self.calendar_object.select_random_recipes(7, group, lock)

        group_user_ids = {}

        for group in group_plans:
            user_ids = await self.get_user_ids(group)
            group_user_ids[group] = user_ids
        
        for group, user_ids in group_user_ids.items():
            recipes = group_plans[group]

            for user_id in user_ids:
                user = await self.bot.fetch_user(user_id)
                meal_plan_text = ""
                for i, recipe in enumerate(recipes, start=1):
                    meal_plan_text += f"**{i}. {recipe['title']}**\n\n{recipe['image']}\n\n"

                view = discord.ui.View()
                for recipe in recipes:
                    view.add_item(RerollButtonView(recipe_id=recipe['id'], group=group))

                view.add_item(ConfirmButtonView(group))
                view.add_item(NewListView(group, self))     

                                         
                

                # print(f'\n\nThis is the recipe ID: {group_plans[group][0]['id']}\n\n')
                # print([r['id'] for r in group_plans[group]])

                await user.send(content = meal_plan_text, view=view)

    


    

