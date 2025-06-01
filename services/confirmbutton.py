import discord
from services.calendar_service import CalendarService

class ConfirmButtonView(discord.ui.View):
    def __init__(self, recipe_id, group):
        super().__init__()
        self.recipe_id = recipe_id
        self.group = group
        self.mealplanner = CalendarService()

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.primary)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        '''
        This function will confirm the mealplan for the user, meaning that it will go through these steps:
        1. All of the recipes are added to a database table
        2. All recipes' times_made column values are incremented by one
        3. Each calendar is added to a subsequent calendar event in the group's calendar
        4. A recipe ingredient list is generated to be shown to the user somewhere

        To accomplish this, this function will be calling many other functions, especially within the CalendarService() object. 
        '''
