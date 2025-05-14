import discord

from discord.ext import commands
from supabase_setup import supabase
from utils.logger import logger
from discord import app_commands



class Register(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='register', description='Register your discord account with a database of recipes.')
    async def register(self, interaction: discord.Interaction, group_number: int):
        if group_number == None:
            interaction.response.send_message(f'Enter a group number!')
            return
        
        user_id = int(interaction.user.id)

        response = supabase.table('users').select('discord_id').eq('discord_id', user_id).execute()

        if response.data:
            await interaction.response.send_message(f'{interaction.user.name} is already added!')
            return
        else:
            
            group_response = supabase.table('groups').select('group').execute()
            existing_group_ids = [g['group'] for g in group_response.data]

            if group_number in existing_group_ids:
                supabase.table('users').insert({
                'group': group_number,
                'discord_id': user_id
                  }).execute()
                await interaction.response.send_message(f'{interaction.user.name} successfully added!')
                
            else:
                supabase.table('groups').insert({
                    'group': group_number
                }).execute()

                supabase.table('users').insert({
                'group': group_number,
                'discord_id': user_id
                }).execute()
                await interaction.response.send_message(f'{interaction.user.name} successfully added!')
            
            
            

            print(response)

           

async def setup(bot):
    await bot.add_cog(Register(bot))
    logger.info('Register cog loaded')
