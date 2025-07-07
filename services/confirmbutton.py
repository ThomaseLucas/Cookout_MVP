import discord
from services.calendar_service import CalendarService
import datetime

class ConfirmButtonView(discord.ui.Button):
    def __init__(self, group, meals):
        super().__init__(label='Confirm', style=discord.ButtonStyle.primary)
        self.group = group
        self.meals = meals
        self.mealplanner:CalendarService = CalendarService()
        self.dates = []
        self.events = []
        self.cal_id = None

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

        if not self.mealplanner.check_if_calendar_exists(self.group):
            self.mealplanner.create_new_calendar(self.group, None)

        self.cal_id = self.mealplanner.get_calendar_id(self.group)
        self.find_dates()
        self.map_data_to_event()

        await interaction.response.send_message(f'Your mealplan has been added to a calendar!').defer()

    def find_dates(self):
        today = datetime.date.today()
        days_ahead = (0 - today.weekday()) % 7  # 0 is Monday
        next_monday = today + datetime.timedelta(days=days_ahead)
        self.dates = [next_monday + datetime.timedelta(days=i) for i in range(8)]

    def map_data_to_event(self):

        for i in range(len(self.dates) - 1):
            self.mealplanner.create_event(self.group, self.meals[i]['title'], self.meals[i]['description'], self.meals[i]['ingredients'], self.meals[i]['instructions'], self.meals[i]['yields'], self.dates[i], self.dates[i + 1])

        self.mealplanner.share_with_user(self.cal_id, 'thomaselucas2020@gmail.com')

        