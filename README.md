## conduit-staging

A multi-network multi-channel IRC relay.

Allows you to configure more than two networks with more than two channels for messages to be relayed between.
Records users on every configured channel on every configured network.
Remembers all invited users with a rank which the bots will automatically promote them to.

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
 - [x] Security
    - [ ] Prevent impersonation
    - [x] Automatically kick users that are disabled
    - [x] Temporarily ban disabled users if attempting to join too often
    - [ ] Improve/clean up rank checking system.
 - [x] Multiple channel supportt
 - [x] Server connection
   - [x] SSL support
   - [x] Automatically run custom commands on connect/reconnect
   - [ ] More than one bot owner (untested)
   - [x] Autojoin more than one channel
   - [x] Store servers in a configuration file.
 - [ ] Have conduit create its own sqlite database.
 - [ ] Python version check to make sure >3.x is being used.

#### RUNNING/DEVELOPING:
**Requirements:** python3
*Make sure that python3 is being used when launching via pip or python!*
```
python --version
pip --version
```
*If these report python 2.x, substitute pip for pip3 and python for python3 in the following commands.*

**Installing:**
```
git clone https://github.com/unendingPattern/conduit-staging.git
cd conduit-staging
pip install -e .
```

**MySQL Database:**

```
mysql -u root -p conduit < conduit.sql
mysql -u root -p conduit < servers.sql
```

**Files:**
* condit/db/*.py - Database connectors
* conduit/functions.py - Helper functions
* conduit/ircbot.py - IRC bot
* conduit/run.py - Instance launcher
* conduit/cleanup.py - Cleanup service
* conduit/regextest.py - Temporary script for testing user regex (`regextest.py <nick!username@hostmask>`)

**How to use:**
`python conduit/ircbot.py`

**To remove or replace:**
* conduit/run.py - No longer serves a purpose with the new launcher system

**Cleanup service:**
* Monitors for which messages have been relayed to all servers and purges them from the database.

`python conduit/cleanup.py`

#### COMMANDS:

```
- Invite User
Access: bot owner(s)
Command: !invite <nick!username@hostmask> <rank> <network>
Ranks: 0 (banned), 1 (member), 10 (halfop), 100 (op)

- Join Channel
Access: users with a rank above 0
Command: !join <channel>

- User List
Access: users with a rank above 0
Command: !users

- Set Rank 
Access: users with a rank above 100
Command: !rank <user> <rank>
```

#### EXAMPLE USECASE
```

       [DISCORD APPSERVICE]  <->  [MATRIX]  <-> [IRC APPSERVICE]
                                                      ^
                                                      |
                                                      v
                                      Rizon  <-> [LOCAL IRC] <-> Freenode
                                                      ^
                                                      |
                                                      v
                                                  Gamesurge
                                                  
Status: Working and tested.
Conclusion:
* Minor bugs and missing features.
* Functional for daily usage on a private/moderated net.

```

#### KNOWN BUGS:
* messages sometimes get repeated twice (echoes)