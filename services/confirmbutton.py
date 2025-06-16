import discord
from services.calendar_service import CalendarService

class ConfirmButtonView(discord.ui.Button):
    def __init__(self, group, meals):
        super().__init__(label='Confirm', style=discord.ButtonStyle.primary)
        self.group = group
        self.meals = meals
        self.mealplanner = CalendarService()

    async def callback(self, interaction: discord.Interaction):
        '''
        This function will confirm the mealplan for the user, meaning that it will go through these steps:
        1. All of the recipes are added to a database table
        2. All recipes' times_made column values are incremented by one
        3. Each calendar is added to a subsequent calendar event in the group's calendar
        4. A recipe ingredient list is generated to be shown to the user somewhere

        To accomplish this, this function will be calling many other functions, especially within the CalendarService() object. 
        '''

        print(f'\n\n{self.meals}\n\n')

        await interaction.response.send_message(f'This is your meal plan for the week: \n{self.meals[0]}')
