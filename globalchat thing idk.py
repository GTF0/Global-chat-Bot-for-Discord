import discord 
from discord.ext import commands
import os
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents, help_command=None)

@bot.event
async def on_ready():
  print('Successfully logged in as {0.user}'.format(bot))

global_chat_channels = {}

@bot.event
async def on_ready():
    print(f'{bot.user.name} is online.')

    # Check for global chat channels in all servers
    for guild in bot.guilds:
        if str(guild.id) not in global_chat_channels:
            try:
                with open(f'{guild.id}/global_chat.txt', 'r') as f:
                    channel_id = f.read().strip()
                channel = bot.get_channel(int(channel_id))
                global_chat_channels[str(guild.id)] = channel
            except FileNotFoundError:
                pass

@bot.event
async def on_guild_join(guild):
    # Create server directory if it doesn't exist
    try:
        os.mkdir(str(guild.id))
    except FileExistsError:
        pass

@bot.command()
async def setglobalchat(ctx):
    # Set global chat channel for the server
    global_chat_channels[str(ctx.guild.id)] = ctx.channel

    # Write channel ID to file
    with open(f'{ctx.guild.id}/global_chat.txt', 'w') as f:
        f.write(str(ctx.channel.id))

    await ctx.send('Global chat channel set.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Send message to all global chat channels
    for guild_id, channel in global_chat_channels.items():
        try:
            embed = discord.Embed(title=f'{message.author.name}#{message.author.discriminator}', url=f'https://discord.com/users/{message.author.id}', description=message.content, color=0x00ff00)
            embed.set_thumbnail(url=message.author.avatar_url)
            await channel.send(embed=embed)
        except discord.errors.Forbidden:
            owner = message.guild.owner
            await owner.send(f'The global chat message could not be sent in your server because the bot does not have permission to send messages in the global chat channel.\nPlease check the channel permissions and try again.')
        except AttributeError:
            # Global chat channel for the server has not been set
            pass

    await bot.process_commands(message)

@bot.event
async def on_guild_remove(guild):
    # Remove server directory and global chat channel file
    try:
        os.remove(f'{guild.id}/global_chat.txt')
        os.rmdir(str(guild.id))
    except FileNotFoundError:
        pass

@bot.command()
async def stopglobal(ctx):
    guild_id = str(ctx.guild.id)
    channel_id = str(ctx.channel.id)

    # Check if global chat folder exists
    if os.path.exists('global_chat'):
        # Check if guild folder exists
        if os.path.exists(f'global_chat/{guild_id}'):
            # Check if global_chat.txt file exists
            if os.path.exists(f'global_chat/{guild_id}/global_chat.txt'):
                # Open global_chat.txt file
                with open(f'global_chat/{guild_id}/global_chat.txt', 'r') as f:
                    # Read lines from file
                    lines = f.readlines()
                # Remove channel ID from lines
                lines = [line for line in lines if line.strip() != channel_id]
                # Open global_chat.txt file in write mode
                with open(f'global_chat/{guild_id}/global_chat.txt', 'w') as f:
                    # Write updated lines to file
                    f.writelines(lines)
                # Send success message
                embed = discord.Embed(title='Success', color=0x00ff00)
                embed.description = f'Channel removed from global chat list.'
                await ctx.send(embed=embed)
            else:
                # Send error message if global_chat.txt file doesn't exist
                embed = discord.Embed(title='Error', color=0xff0000)
                embed.description = f'Global chat not set up for this server.'
                await ctx.send(embed=embed)
        else:
            # Send error message if guild folder doesn't exist
            embed = discord.Embed(title='Error', color=0xff0000)
            embed.description = f'Global chat not set up for this server.'
            await ctx.send(embed=embed)
    else:
        # Send error message if global_chat folder doesn't exist
        embed = discord.Embed(title='Error', color=0xff0000)
        embed.description = f'Global chat not set up for this server.'
        await ctx.send(embed=embed)


@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    
    # Create server folders if they don't exist
    for guild in bot.guilds:
        guild_folder = os.path.join(os.getcwd(), guild.id)
        if not os.path.exists(guild_folder):
            os.makedirs(guild_folder)

@bot.event
async def on_message(message):
    # Check if message is from a global chat channel
    if message.channel.id in global_chat_channels:
        # Get server folder
        server_folder = os.path.join(os.getcwd(), message.guild.id)
        
        # Create chatlogs folder if it doesn't exist
        chatlogs_folder = os.path.join(server_folder, "chatlogs")
        if not os.path.exists(chatlogs_folder):
            os.makedirs(chatlogs_folder)
        
        # Log message to appropriate log file
        with open(os.path.join(chatlogs_folder, f"{message.author.id}.txt"), "a") as f:
            f.write(f"{message.author.id} - {message.content} - {message.jump_url}\n")        


@bot.command()
@commands.cooldown(1, 1800, commands.BucketType.user)
async def report(ctx, reported_user: discord.Member, *, reason):
    embed = discord.Embed(title=f"Are you sure you want to report {reported_user.name}?", description=f"Reason: {reason}", color=0xFF0000)
    embed.set_footer(text=f"Report will be sent to moderators for review.")
    
    msg = await ctx.send(embed=embed)
    await msg.add_reaction('✅')
    await msg.add_reaction('❌')
    
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == msg.id
    
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await msg.delete()
        return
    
    if str(reaction.emoji) == '✅':
        embed = discord.Embed(title="Thank you for your report", description="Our moderation team will review this report as soon as possible.", color=0x00FF00)
        await msg.edit(embed=embed)
        
        # Send evaluation of report to the designated channel
        channel = bot.get_channel(1084951057282646077)
        embed = discord.Embed(title=f"Report from {ctx.author.name}", description=f"Reported user: {reported_user.mention}\nReason: {reason}\n\nMessages sent by reported user in global chat:")
        
        # Get the log file for the server and reported user
        server_folder = f"chatlogs/{ctx.guild.id}"
        user_file = f"{server_folder}/{reported_user.id}.txt"
        
        try:
            with open(user_file, 'r') as file:
                messages = file.readlines()
                messages.reverse()  # Reverse to show most recent messages first
                for line in messages:
                    embed.add_field(name="\u200b", value=line)
                
                # Send the log file to the server
                with open(f"{reported_user.name} chatlog.txt", 'w') as f:
                    f.write(''.join(messages))
                await ctx.author.send(f"Here's the chat log for {reported_user.name} in this server.", file=discord.File(f"{reported_user.name} chatlog.txt"))
        except FileNotFoundError:
            embed.add_field(name="\u200b", value="No messages found.")
        
        await channel.send(embed=embed)
        
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == '✅' and reaction.message.id == msg.id
        
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            return
        
        if str(reaction.emoji) == '✅':
            # Blacklist the reported user
            await ctx.send(f"{reported_user.mention} has been blacklisted from sending messages in global chat.")
        else:
            return
        
    else:
        embed = discord.Embed(title="Report cancelled", color=0xFF0000)
        await msg.edit(embed=embed)

@report.error
async def report_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(title="Slow down", description=f"You can report again in {error.retry_after} seconds.", color=discord.Color.red())
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Error", description="Something went wrong, please try again later.", color=discord.Color.red())
        await ctx.send(embed=embed)

@bot.command()
async def globalrules(ctx):
    embed = discord.Embed(title="Global Chat Rules", color=0xFF5733)
    embed.set_thumbnail(url="https://i.imgur.com/UqmkfVb.png")
    embed.add_field(name="1. No Spamming", value="Do not send multiple messages in a row.")
    embed.add_field(name="2. No NSFW content", value="Do not send any NSFW content in the global chat channels.")
    embed.add_field(name="3. No Personal Attacks or Harassment", value="Respect others and do not harass or attack them.")
    embed.add_field(name="4. No Advertising", value="Do not advertise anything in the global chat channels.")
    embed.add_field(name="5. Stay on Topic", value="Keep your messages relevant to the topic of the global chat channel.")
    embed.set_footer(text="Please follow these rules to keep the global chat channels enjoyable for everyone.")
    await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot: # ignore bot messages
        return

    # check if message was sent in a global chat channel
    if message.channel.id in global_chat_channels:

        # get user's nickname or username
        username = message.author.nick or message.author.name

        # construct embed
        embed = discord.Embed(title=f"Message from {username}", description=message.content)
        embed.set_footer(text=f"User ID: {message.author.id} | Message ID: {message.id}")

        # send embed to log channel
        log_channel = bot.get_channel(1084951057282646077)
        await log_channel.send(embed=embed)

        # delete user's message
        await message.delete()

    await bot.process_commands(message) # process other bot commands

@bot.command()
@commands.is_owner()
async def globalwarn(ctx, user: discord.User):
    # Send warning message to the user
    await user.send("You have received a warning for violating the rules in global chat channels. Please review the rules and abide by them in the future.")
    # Send confirmation message in the channel
    await ctx.send(f"Warning has been sent to {user.mention}")

@bot.command()
async def globalinfo(ctx):
    embed = discord.Embed(title="Global Chat Information", color=0x00ff00)
    embed.add_field(name="What is Global Chat?", value="Global chat is a feature that allows users to communicate with other users in different servers using shared channels.", inline=False)
    embed.add_field(name="How to use Global Chat?", value="To use global chat, simply join a shared global chat channel and start typing. Your message will be sent to all servers that have that same global chat channel.", inline=False)
    embed.add_field(name="Rules for Global Chat", value="Make sure to read and follow the rules for using global chat in each server. Violating these rules can result in warnings, kicks, or even a permanant blacklist.", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def globalstats(ctx):
    guild = ctx.guild
    # Get all global chat channels in the server
    global_channels = [channel for channel in guild.channels if channel.name.startswith('global-')]
    num_global_channels = len(global_channels)
    # Get the number of users who have sent a message in a global chat channel
    users_with_messages = set()
    for channel in global_channels:
        async for message in channel.history():
            users_with_messages.add(message.author)
    num_users_with_messages = len(users_with_messages)
    # Create and send the embed
    embed = discord.Embed(title="Global Chat Stats", color=discord.Color.blue())
    embed.add_field(name="Number of Global Chat Channels", value=num_global_channels)
    embed.add_field(name="Number of Users who have Sent a Message in Global Chat", value=num_users_with_messages)
    await ctx.send(embed=embed)

@bot.command() ## lists all commands the bot has. 
async def help(ctx):
  # Create a list of all the commands
  commands = []
  for command in bot.commands:
    commands.append(f"**{command.name}**: {command.help}")

  # Divide the commands into pages of 10 commands each
  pages = [commands[i:i+10] for i in range(0, len(commands), 10)]

  # Set the initial page
  page = 0

  # Create the embed message
  embed = discord.Embed(title="Commands",
                        description="\n".join(pages[page]),
                        color=0x00ff00)

  # Send the embed message
  message = await ctx.send(embed=embed)

  # Add the emoji reactions
  await message.add_reaction("⏪")
  await message.add_reaction("⏩")

  # Wait for a reaction
  def check(reaction, user):
    return user == ctx.author and str(reaction.emoji) in ["⏪", "⏩"]

  while True:
    try:
      reaction, user = await bot.wait_for("reaction_add", check=check, timeout=60)
    except asyncio.TimeoutError:
      # Remove the emoji reactions after 60 seconds
      await message.clear_reactions()
      break
    else:
      # Update the page based on the reaction
      if str(reaction.emoji) == "⏪":
        page = max(page-1, 0)
      elif str(reaction.emoji) == "⏩":
        page = min(page+1, len(pages)-1)

      # Update the embed message
      embed = discord.Embed(title="Commands",
                            description="\n".join(pages[page]),
                            color=0x00ff00)
      embed.set_footer(text=f"Page {page+1}/{len(pages)}")
      await message.edit(embed=embed)



bot.run('enter your bot token here')