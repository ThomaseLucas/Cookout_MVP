import discord
# from services.calendar_service import CalendarService

class NewListView(discord.ui.View):
    def __init__(self, group, meal_plan_object):
        super().__init__()
        self.group = group
        self.planner = meal_plan_object

    @discord.ui.button(label='New List', style=discord.ButtonStyle.primary)
    async def reroll(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(self.recipe_id, self.group)
        new_recipes =  self.planner.run_meal_plan_for_all_groups(self.group)
        print(new_recipes)
        # await interaction.response.edit_message(content=f'New Recipe: {new_recipe[0]['title']}')
