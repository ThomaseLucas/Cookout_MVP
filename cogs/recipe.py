import discord
import utils.logger
from discord.ext import commands
from discord import app_commands 
from utils.logger import logger
from recipe_scrapers import scrape_me
from supabase_setup import supabase
import time
from datetime import datetime

class AddRecipeGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name='add_recipe', description='Add a recipe manually or by url')

    @app_commands.command(name='manual', description='Add a recipe by typing it in')
    async def manual(self, interaction: discord.Interaction):

        await interaction.response.send_message(
            f'This manual command is working!', 
            ephemeral=True)

    @app_commands.command(name='url', description='Add a recipe by providing a link')
    async def url(self, interaction: discord.Interaction, link: str):
        
        user_id = int(interaction.user.id)
        
        response = supabase.table('users').select('group').eq("discord_id", user_id).execute()
        
        if response.data:

            #print(response)

            timestamp = time.time()
            datetime_object = datetime.fromtimestamp(timestamp)

            recipe = self._extract_recipe(link)

            if not recipe:
                await interaction.response.send_message(f'Our program isn''t compatiable with this website. Please enter it manually', ephemeral=True)
                return

            duplicate = supabase.table('recipes').select('title').eq('title', recipe['title']).eq('group', response.data[0]['group']).execute()

            if duplicate.data:
                await interaction.response.send_message(f'{recipe['title']} is already in the group:{response.data[0]['group']}')
                return
                    
            print(recipe['description'])

            supabase.table('recipes').insert({
                'added_by': interaction.user.name,
                'added_at': str(datetime_object),
               'title': recipe['title'],
                'ingredients': recipe['ingredients'],
                'instructions': recipe['instructions'],
                'total_time': recipe['total_time'],
                'description': recipe['description'],
                'image': recipe['image'],
                'yields': recipe['yields'],
                'group': response.data[0]['group']
            }).execute()

            await interaction.response.send_message(f'{recipe['title']} successfully added to group {response.data[0]['group']}', embed=discord.Embed().set_image(url=recipe['image']))
                
            
        else:
            await interaction.response.send_message(f'{interaction.user.name} not found! Please register your account to a group using "/register [group number]"')
            
        
    def _extract_recipe(self, url):
        '''
        Inputs:
        - url

        Functionality: 
        - This function is here as a helper function to allow the main logic to get a dictionary of differnet objects that contain the important things in a recipe such as ingredients and steps

        Output:
        - A dictionary of different attributes of the recipe
        '''
        try:
            scraper = scrape_me(url)

            #retrieves data from website using recipe_scrapers library
            return {
                'title': scraper.title(),
                'ingredients': scraper.ingredients(),
                'instructions': scraper.instructions(),
                'total_time': scraper.total_time(),
                'description': scraper.description(),
                'image': scraper.image(),
                'url': scraper.url,
                'yields': scraper.yields()
            }
        except Exception as e:
            print(f'Scrape failed. Unexpected error: {e}')
            return None
        

class RecipeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.add_command(AddRecipeGroup())

async def setup(bot):
    await bot.add_cog(RecipeCog(bot))
    logger.info('Recipe cog loaded')
