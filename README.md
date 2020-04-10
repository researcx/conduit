## conduit-staging

A multi-network multi-channel IRC relay.

* Allows you to configure more than two networks with more than two channels for messages to be relayed between.
* Records users on every configured channel on every configured network.
* Remembers all invited users with a rank which the bots will automatically attempt to promote them to.
* Provides useful commands for administrators to manage their linked servers with.

**Warning:** Experimental software.

#### FEATURES & ROADMAP:
 - [x] Server <-> Server
     - [x] Messages (PRIVMSG)
     - [x] Actions (ACTION)
     - [x] Joins (JOIN)
     - [x] Parts (PART)
     - [ ] Kicks (KICK)
     - [ ] Quits (QUIT)
     - [ ] Private Messages
 - [x] Notifications
    - [x] Join/leave notifications
    - [x] List all users on the channel to newly joined person
 - [x] User system
   - [x] Invite system
   - [x] User list
   - [ ] User Profiles (!info `<user>`)
   - [x] Automatic rank promotion/demotion
   - [ ] Manual registration
   - [x] Change rank commands (!disable `<user>`, !rank `<user>` `<rank>`)
   - [x] Join command
 - [x] Security
    - [ ] Prevent impersonation
    - [x] Automatically kick users that are disabled
    - [ ] Temporarily ban disabled users if attempting to join too often
    - [ ] Improve/clean up rank checking system
    - [ ] Fakelag to prevent message/command flood
    - [x] Permission checking for running commands
    - [ ] More than one bot owner (untested)
    - [x] Give bot owners rank 1000
 - [x] Multiple channel support
 - [x] Server connection
   - [x] SSL support
   - [x] Automatically run custom commands on connect/reconnect
   - [x] Autojoin more than one channel
   - [x] Store servers in a configuration file
   - [ ] Cleanup process to be automatically ran with the bot
 - [ ] Have conduit create its own sqlite database
 - [ ] Python version check to make sure >3.x is being used

#### RUNNING/DEVELOPING:
**Requirements:** python3, mysql server
*Make sure that python3 is being used when launching via pip or python!*
```
python --version
pip --version
```
*If these report python 2.x, substitute pip for pip3 and python for python3 in the following commands.*

**Installation:**
```
git clone https://github.com/unendingPattern/conduit-staging.git
cd conduit-staging
pip install -e .
```

**Setting up the MySQL Database:**

```
mysql -u root -p conduit < conduit.sql
```

**Usage:**

Edit `conduit/data/bot.cfg`

Run `python conduit/ircbot.py`

#### RANKS:
```
0 (banned), 1 (member), 10 (halfop), 100 (op), 1000 (admin)
```

#### COMMANDS:
```
- Join Channel
Private messaging the bot with this has the bot invite you to the channel.
Access: users with a rank above 0
Command: !join <channel>

- User List
Lists all users in the current channel on every configured network.
Access: users with a rank above 0
Command: !users

- Invite User
Invites a user to the current channel.
Access: users with a rank of 1000 (admins)
Command: !invite <nick!username@hostmask> <rank>

- Set Rank
Sets a user rank for the current channel.
Access: users with a rank of 1000 (admins)
Command: !rank <user> <rank>

- Disable
Disables a user by setting their rank to 0 in the current channel.
Access: users with a rank of 1000 (admins)
Command: !disable <user>

- Enable
Enables a user by setting their rank to 1 in the current channel.
Access: users with a rank of 1000 (admins)
Command: !enable <user>
```

#### EXAMPLE USECASE
```

[DISCORD APPSERVICE]  <->  Matrix Server  <-> [IRC APPSERVICE]
        ^                                            ^
        |                                            |
        v                                            v
  Discord Server                      Rizon  <->  LocalIRC <-> Freenode
                                                     ^
                                                     |
                                                     v
                                                 GameSurge
                                                  
Status: Working and tested.
Conclusion:
* Functional for daily usage on a private/moderated net.
* Experimental software.

```

#### KNOWN BUGS:
* messages sometimes get repeated twice (echoes)