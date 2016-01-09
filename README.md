#Decision-Bot.py

01/09/2016
This is a bot for a Discord server. This bot has functions that cater mainly to PSO2. It has the ability to shout at everyone whenever an EQ is coming up and it has the ability to organize multi-parties.

I do not know if this bot is heroku-compatible. I haven't tried it and will not try it. If you do try it though, get back to me about it and do tell me how it works out.

There are several base commands that the bot has. Any command listed with the notion [M] means that it can only be used by a user with a role that can manage channels. 

BASIC COMMANDS:
!help - spits out a wall of text that tells the users what the bot is capable of and what commands users are allowed to use
!hello - replies to the user with a simple hello.
!fuckyou - replies to the user with a simple fuck you.
!eq - posts the current EQ status that comes straight from Flyergo's API.

EQ COMMANDS:
!startmpa [M] - Starts an MPA in the channel it is called in. Usually called by the bot automatically.
!removempa [M] - Frees the MPA list from memory and deletes the channel.
!addme - adds the user who calls this command into the MPA.
!removeme - removes the user who calls this command from the MPA.
!addplayer [M] - adds the string that is specified within the call to the MPA list.
!removeplayer [M] - removes the string OR user that is specified within the call from the MPA list.

DEBUG COMMANDS:
!id - gives the user it's unique ID that is assigned to their account.
!startparse - Called automatically once the bot has started. But starts the EQ-notification function.


You will need the following API to get the bot working: https://github.com/Rapptz/discord.py

MUCH LOVE TO RAPPTZ FOR THE WONDERFUL API.

MUCH LOVE TO ACF FOR POINTING ME AT THE RIGHT DIRECTION.

MUCH LOVE TO FLYERGO FOR THE WEBAPI THAT HE IS RUNNING.

