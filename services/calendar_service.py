from services.calendar_setup import get_calendar_service
from supabase_setup import supabase
import datetime
import random
import asyncio

class CalendarService():
    def __init__(self):
        self.gcs = get_calendar_service() #stands for Google Calendar Service, just didn't want to type that out every time
        self.supabase_connection = supabase

        self.sharing_rule = {
                'scope': {
                    'type': 'default'
                },
                'role':'reader'
            }
        
    def get_calendar_id(self, group):
        '''This gets the id of the calendar that is attached to the group in the database'''

        get_id_query = supabase.table('groups').select('google_calendar_id').eq('group', group) 
        result = get_id_query.execute()
        return result.data[0]['google_calendar_id']
        
    def check_if_calendar_exists(self, group, name=None):
        '''This checks if there is a calendar that belongs to a group'''
        if name == None:
            calendar_group_id = self.get_calendar_id(group)
            if calendar_group_id is None:
                self.create_new_calendar(group, None)
                return False
            else:
                return True                
            
        else:
            calendar_group_id = self.get_calendar_id(group)
            
            if calendar_group_id is None:
                self.create_new_calendar(group, name)
                return False
            else:
                return True   
                

    def create_new_calendar(self, group, name):
        '''This function creates a new calendar according to the group. If the group doesn't have a name, the name of the calendar will be the group number
        Input: group number
        Output: creation of a calendar, that appends it to a list of calendars in the google workspace. (If this ever becomes an app I'm not sure how I would do this.)
        '''

        if name == None:
            calendar = {
                'summary': f'Group: {group}',
                'timeZone': 'America/Denver'
            }

            created_calendar = self.gcs.calendars().insert(body=calendar).execute()
            calendar_id = created_calendar['id'] 
            print(calendar_id)

            self.gcs.acl().insert(calendarId=calendar_id, body=self.sharing_rule).execute()

            result = supabase.table('groups') \
            .update({'google_calendar_id': calendar_id}) \
            .eq('group', int(group)) \
            .execute()
            # print(result.data)

        else:
            calendar = {
                'summary': f'Group: {group}',
                'timeZone': 'America/Denver'
            }

            created_calendar = self.gcs.calendars().insert(body=calendar).execute()
            calendar_id = created_calendar['id'] 
            print(calendar_id)

            self.gcs.acl().insert(calendarId=calendar_id, body=self.sharing_rule).execute()

            result = supabase.table('groups') \
            .update({'google_calendar_id': calendar_id}) \
            .eq('group', int(group)) \
            .execute()
            # print(result.data, result.count)

        
    def create_event(self, group, title, description, ingredients, instructions, yeilds, start_date, end_date, image=None, ):
        '''This function simply creates an event on a calendar, in the context of a recipe. These args will be random from the database, but once they get here, we just make an event with this information'''
        event = {
            'summary': title,
            'description': f'''
            {description}

            **Ingredients**
            {chr(10).join(ingredients)}

            **Instrutcions**
            {instructions}

            **Yields**
            {yeilds}
            ''',
            'start': {
                'date': start_date.isoformat(),
                'timeZone': 'America/Denver'
            },
            'end': {
                'date': end_date.isoformat(),
                'timeZone': 'America/Denver'
            }
        }   
        
        calendar_id = self.get_calendar_id(group)
        created_event = self.gcs.events().insert(calendarId=calendar_id, body=event).execute()

        # print(f'Event Created', created_event.get('htmlLink'))

    async def select_random_recipes(self, days_needed, group, meal_plan_lock, reroll_recipe=None):
        '''This method selects a number of random recipes where they haven't been used this month yet, where they match the group number. This will return a list of dictionaries of the  recipe id and title'''
        async with meal_plan_lock:

            recipes = []
            final_recipes = []
            times_made = 0

            if reroll_recipe:
                return self.select_random_recipes(1, group)

            while True: 

                if times_made == 10:
                    return 'Not enough recipes in the database! Please add more.' #makes sure no infinite loop is possible, you shouldn't be eating 1 recipe 10 times in a month.
                
                total_recipes = supabase.table('recipes').select('id, title, description, image, ingredients, instructions, total_time, yields', count="exact").eq('group', group).eq('times_made', times_made).execute() #grabs all recipes where they've been made equal to the times_made variable

                # print(total_recipes)
                # print()
                # print(total_recipes.count)

                if total_recipes.count == 0: #checks if the count is 0, if so, increment the times_made 1 more
                    times_made += 1
                    continue

                

                if int(total_recipes.count) + int(len(recipes)) < days_needed: # If the amount of recipes found from the query and the length of the list is still less than the amount of days needed, add all of the query recipes to the list, and then reiterate
                    recipes.extend(total_recipes.data)
                    times_made += 1
                    continue

                else:
                    recipes.extend(total_recipes.data)
                    break

            random_ints_used = []
            while len(final_recipes) < days_needed:
                random_index = random.randint(0, len(recipes) - 1)

                if random_index not in random_ints_used:
                    final_recipes.append(recipes[random_index])
                    random_ints_used.append(random_index)

            return final_recipes
                
            
    def share_with_user(self, calendar_id, email_to_share):
        # print(f'[SHARING] {calendar_id} with {email_to_share}')

        try:
            self.gcs.acl().insert(calendarId=calendar_id, 
                                body={
                                    'scope':{
                                        'type':'user',
                                        'value': 'thomaselucas2020@gmail.com'
                                    },
                                    'role': 'reader'
                                }).execute()
            
            # print(f'Successfully shared with {email_to_share}\n')
            # print(f"https://calendar.google.com/calendar/u/0/r?cid={calendar_id}")
            return f"https://calendar.google.com/calendar/u/0/r?cid={calendar_id}"

        except Exception as e:
            print(f'An error occured: {e}')

            

    
    def create_number_of_events(self, amount):
        pass
    def reroll_recipe(self, recipe_id, group):
        times_made_counter = 0

        while True:
            print(f'Recipe rerolled! {recipe_id} {group}')
            response = supabase.table('recipes').select('id, title, description, image, ingredients, instructions, total_time, yields').eq('group', group).eq('times_made', times_made_counter).neq('id', int(recipe_id)).execute()
            
            if response.data:
                break
            else:
                times_made_counter += 1

        length = len(response.data)

        random_index = random.randint(0, length - 1)
        print(response.data[random_index])
        return response.data[random_index]
        
    def reroll_all_week(self):
        pass
    
