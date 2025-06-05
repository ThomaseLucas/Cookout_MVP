from services.calendar_service import CalendarService
from supabase_setup import supabase
from datetime import datetime, timezone
import asyncio
from services.reroll import RerollButtonView
from services.newlistbutton import NewListView
from services.confirmbutton import ConfirmButtonView
import discord
from config import GUILD_ID 



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

    def track_messages(self, group, message_ids):
        pass

    def get_groups_to_plan(self, group):
        groups_to_plan = []

        group_query = supabase.table('groups').select('*').execute() #This query gets the group numbers which haven't had a meal plan made in 7 days. 
        for data in group_query.data:
            result = self.check_for_expired_date(data) 
            if result:
                groups_to_plan.append(result) #creates a list of all the groups that we need a meal plan for

        return groups_to_plan
    
    async def map_meal_plans(self, groups_to_plan, lock):
        group_plans = {} #This dictionary is here to store the meal plan for each group. Structure: group_plans[1] = [{'title': 'Pizza'}, {'ingredients': 'Cheese'}]
        for group in groups_to_plan:
            if group not in group_plans:
                group_plans[group] = [] 
            
            group_plans[group] = await self.calendar_object.select_random_recipes(7, group, lock) #creates a list of objects that holds the title and id of the recipe for later calling to be able to show the user, and fill out a calendar.

        return group_plans

    async def map_group_users(self, group_plans):
        group_user_ids = {}
        
        for group in group_plans:
            user_ids = await self.get_user_ids(group)
            group_user_ids[group] = user_ids

        return group_user_ids
    

    async def get_or_create_group_channel(self, guild, group, user_ids):
        print(user_ids)
        channel_name = f'meal-plan-group-{group}'
        existing = discord.utils.get(guild.text_channels, name=channel_name)

        if existing:
            return existing
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
        }

        members = guild.members
        for m in members: 
            print(f'adding member {m.name}: {m.id}')
            if str(m.id) in user_ids:
                overwrites[m]= discord.PermissionOverwrite(read_messages=True, send_messages=True)
        print(overwrites)
        return await guild.create_text_channel(name=channel_name, overwrites=overwrites)


    async def send_meal_plans_to_users(self, group_plans, group_user_ids):
        
        for group, user_ids in group_user_ids.items():
            recipes = group_plans[group]
            changing_recipes = {}

            for recipe in recipes:
                changing_recipes[recipe['title']] = recipe

            print(changing_recipes)

            guild = self.bot.get_guild(int(GUILD_ID))
            if guild != None:
                print(guild.members)
                channel = await self.get_or_create_group_channel(guild, group, user_ids)
            else:
                print('Guild not found.')

            view = discord.ui.View()
            await channel.purge(limit=100)

            for i, recipe in enumerate(recipes, start=1):
                embed = discord.Embed(
                title=recipe['title'],
                description=recipe['description'],
                color=discord.Color.green()
            )
                embed.set_image(url=recipe['image'])

                view = discord.ui.View()
                view.add_item(RerollButtonView(recipe_id=recipe['id'], group=group, recipe_title=recipe['title'], changing_recipes=changing_recipes)) 
                print(f'{i}. **{recipe['title']}')

                try:
                    await channel.send(embed=embed, view=view)
                except discord.HTTPException:
                    print(f'Failed to send message to group: {group}')
                    await asyncio.sleep(1.5)
                    await channel.send(embed=embed, view=view)


            final_view = discord.ui.View()

            final_view.add_item(ConfirmButtonView(group))
            final_view.add_item(NewListView(group, self)) #TODO make logic to be able to not repeat the same meals when using the new_list button

            await channel.send(view=final_view)
    


    async def run_meal_plan_for_all_groups(self, group=None):
        if not group:
            group_query = supabase.table('groups').select('*').execute() #This query gets the group numbers which haven't had a meal plan made in 7 days. 
            groups_to_plan = [self.check_for_expired_date(data) for data in group_query.data if self.check_for_expired_date(data)]
            
        else:
            groups_to_plan = [group]
        
        lock = asyncio.Lock()
        try:
            group_plans = await self.map_meal_plans(groups_to_plan, lock)
        except Exception as e:
            print(f'Failed to map meals to plans: {e}')

        try:
            group_user_ids = await self.map_group_users(group_plans)
        except Exception as e:
            print(f'Failed to map users: {e}')

        try:
            await self.send_meal_plans_to_users(group_plans, group_user_ids)
            print('reached the end of meal planning')
        except Exception as e:
            print(f'Failed to send message: {e}')

    


    

