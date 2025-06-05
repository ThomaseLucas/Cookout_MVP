import discord
# from services.calendar_service import CalendarService

class NewListView(discord.ui.Button):
    def __init__(self, group, meal_plan_object):
        super().__init__(label='New Plan', style=discord.ButtonStyle.primary)
        self.group = group
        self.planner = meal_plan_object

    async def callback(self, interaction: discord.Interaction):
        await self.planner.run_meal_plan_for_all_groups(self.group)
