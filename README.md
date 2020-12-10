# BotColosseum

An environment to allow for bot writing competitions

I wrote this in a way to allow for sandboxing later on. When a bot is run, it is spawned in a new process which communicates with the parent via stdin/stdout. Currently, the bot is called using python3 but this can be changed to an interpreter that allows for sandboxing such as PyPy. 
