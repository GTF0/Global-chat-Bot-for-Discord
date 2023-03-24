# Global-chat-Bot-for-Discord
This is a Global chat Discord Bot written in Python.

# Global Chat Bot

This is a Discord bot that allows users to communicate across servers using global chat channels. The bot can be configured to log and synchronize messages sent in these channels, and also includes moderation features such as reporting, warning, and banning users.

## Features

### Global Chat Channels

The bot allows users to communicate across servers using designated global chat channels. These channels can be created using the `createglobalchannel` command.

### Message Logging and Synchronization

The bot can be configured to log and synchronize messages sent in global chat channels. Each server has its own log file, which can be accessed using the `globallog` command. The bot checks for new messages every 5 seconds and syncs them to the appropriate log file.

### Reporting

Users can report other users for violating the rules in global chat channels using the `report` command. The bot sends a warning message and prevents the user from submitting another report for 30 minutes if they try to abuse this feature. The report is sent to a designated mod channel for review.

### Warning and Banning

The bot includes commands for warning and banning users who violate the rules in global chat channels. These commands can only be used by the bot owner. Users who are banned from global chat channels are prevented from sending messages in any channel that has been designated as a global chat channel.

### Global Chat Rules and Information

The bot includes commands for displaying the rules and information about the global chat feature in a server. These commands can be used by any user.

### Global Chat Statistics

The bot includes a command for displaying statistics related to global chat usage in a server.



## Usage
To use the bot, you must have a Discord server and have the necessary permissions to add a bot to your server.

1. Create a new Discord bot and add it to your server. You can follow these instructions to do this. https://discordpy.readthedocs.io/en/latest/discord.html
2. Copy the contents of `blacklist_bot.py` into a new file in your preferred text editor.
3. Replace channel ID with your actual channel ID where you want the reports to be sent.

## Contributing

Contributions to this project are welcome! If you find a bug or have a feature request, please create an issue in the repository or submit a pull request.

## License

This project is licensed under the MIT License 


Note: Just a quick note that the global chat bot has been updated to create the necessary folders and files for each server automatically. This means you don't need to worry about setting anything up yourself.

Thanks for using the bot!
Feel free to contact me under zozyzop@gmail.com for any help or inquires regarding any problem / question / any suggestion that you may have.

(only works on windows)
