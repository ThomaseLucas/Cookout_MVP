import discord
from services.calendar_service import CalendarService

class RerollButtonView(discord.ui.View):
    def __init__(self, recipe_id, group):
        super().__init__()
        self.recipe_id = recipe_id
        self.group = group
        self.mealplanner = CalendarService()

    @discord.ui.button(label='Reroll', style=discord.ButtonStyle.primary)
    async def reroll(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(self.recipe_id, self.group)
        new_recipe =  self.mealplanner.reroll_recipe(self.recipe_id, self.group)
        print(new_recipe)
        await interaction.response.edit_message(content=f'New Recipe: {new_recipe[0]['title']}')
