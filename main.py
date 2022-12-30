import discord
from discord import app_commands
import os
import sqlite3
import botConfig

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

con = sqlite3.connect('classes.db')
cur = con.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS classes (name TEXT, description TEXT)')
con.commit()

# Switch case, if botConfig.enviro is dev, set guild ID to 614524029381902357, if it's prod set it to 743809429039874108
if botConfig.enviro == 'dev':
    guild = discord.Object(id=614524029381902357)
elif botConfig.enviro == 'prod':
    guild = discord.Object(id=743809429039874108)

@client.event
async def on_ready():
    await tree.sync(guild=guild)
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

async def checkAdmin(interaction):
    return not discord.utils.get(interaction.user.roles, name='Admin') and not discord.utils.get(interaction.user.roles, name='Moderator')

@tree.command(name = 'createclass', description = 'Create a class', guild=guild)
async def createclass(interaction, name: str, description: str):
    createClassCur = con.cursor()
    """Create a class"""
    # Check if user has Admin or Moderator role
    if await checkAdmin(interaction):
        await interaction.response.send_message('You do not have permission to use this command')
        return
    # Check if class already exists
    if discord.utils.get(interaction.guild.roles, name=name) or discord.utils.get(interaction.guild.categories, name=description):
        await interaction.response.send_message('Class already exists')
        return
    guild = interaction.guild
    await guild.create_role(name=name)
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        # Set the permissions for the role
        discord.utils.get(guild.roles, name=name): discord.PermissionOverwrite(read_messages=True)
    }
    await guild.create_category(name=description, overwrites=overwrites)
    category = discord.utils.get(guild.categories, name=description)
    await guild.create_text_channel(name=description, category=category, overwrites=overwrites)
    await guild.create_voice_channel(name=description, category=category, overwrites=overwrites)
    # Insert class into database
    createClassCur.execute('INSERT INTO classes VALUES (?, ?)', (name, description))
    con.commit()
    await interaction.response.send_message('Class "' + name + " " + description + '" created')

@tree.command(name = 'deleteclass', description = 'Delete a class', guild=guild)
async def deleteclass(interaction, name: str):
    """Delete a class"""
    deleteClassCur = con.cursor()
    # Check if user has Admin or Moderator role
    if await checkAdmin(interaction):
        await interaction.response.send_message('You do not have permission to use this command')
        return
    # Check if class exists
    if not discord.utils.get(interaction.guild.roles, name=name):
        await interaction.response.send_message('Class does not exist')
        return
    # Delete class
    role = discord.utils.get(interaction.guild.roles, name=name)
    await role.delete()
    # Delete text and voice channel
    # Grab class description from database
    deleteClassCur.execute('SELECT description FROM classes WHERE name = ?', (name,))
    description = deleteClassCur.fetchone()[0]
    category = discord.utils.get(interaction.guild.categories, name=description)
    for channel in category.channels:
        await channel.delete()
    await category.delete()
    # Delete class from database
    deleteClassCur.execute('DELETE FROM classes WHERE name = ?', (name,))
    con.commit()
    await interaction.response.send_message('Class "' + name + '" deleted')

@tree.command(name = 'addclass', description = 'Add a class', guild=guild)
async def addclass(interaction, name: str):
    """Add a class"""
    addClassCur = con.cursor()
    # Check that class exists in database
    addClassCur.execute('SELECT name FROM classes WHERE name = ?', (name,))
    allowed_roles = [x[0] for x in addClassCur.fetchall()]
    if name not in allowed_roles:
        await interaction.response.send_message('Class does not exist')
        return
    # Check if user already has the class
    if discord.utils.get(interaction.user.roles, name=name):
        await interaction.response.send_message('You already have this class')
        return
    # Add the class to the user
    role = discord.utils.get(interaction.guild.roles, name=name)
    await interaction.user.add_roles(role)
    await interaction.response.send_message('Class "' + name + '" added')

@tree.command(name = 'removeclass', description = 'Remove a class', guild=guild)
async def removeclass(interaction, name: str):
    removeClassCur = con.cursor()
    """Remove a class"""
    # Check that class exists in database
    removeClassCur.execute('SELECT name FROM classes WHERE name = ?', (name,))
    allowed_roles = [x[0] for x in removeClassCur.fetchall()]
    if name not in allowed_roles:
        await interaction.response.send_message('Class does not exist')
        return
    # Check if user has the class
    if not discord.utils.get(interaction.user.roles, name=name):
        await interaction.response.send_message('You do not have this class')
        return
    # Remove the class from the user
    role = discord.utils.get(interaction.guild.roles, name=name)
    await interaction.user.remove_roles(role)
    await interaction.response.send_message('Class "' + name + '" removed')

client.run(botConfig.token)