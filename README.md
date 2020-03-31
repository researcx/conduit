## conduit-staging

A multi-network multi-channel IRC relay.

Allows you to configure more than two networks with more than two channels for messages to be relayed between.
Records users on every configured channel on every configured network.
Remembers all invited users with a rank which the bots will automatically promote them to.

#### FEATURES & ROADMAP:
 - [x] Server -> Server
     - [x] Messages (PRIVMSG) (100%)
     - [x] Actions (ACTION) (100%)
     - [ ] Private Messages
 - [ ] Notifications
    - [ ] Join/part (x has joined #x on x, x has left #x on x)
    - [ ] List all users on the channel to newly joined person
 - [ ] Security
    - [ ] Prevent impersonation
 - [x] User system (90%)
   - [x] Invite system
   - [x] User list (90%)
   - [ ] User Profiles (!info `<user>`)
   - [ ] Automatic rank promotion
   - [ ] Registration
   - [ ] Change rank commands (!ban `<user>`, !promote `<user>`, !demote `<user>`, !setrank `<user>` `<rank>`)
 - [x] Multiple channel support (untested)
 - [x] Server connection (90%)
   - [x] SSL support
   - [ ] Automatically run commands on connect/reconnect
   - [ ] More than one bot owner
   - [ ] Autojoin more than one channel
   - [ ] Script to add and modify servers in the database
   - [ ] OR move servers out from the database to be stored in a configuration file.
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

**Instance launcher:**
* Launches multiple instances based on servers stored in the database.
* Also runs the cleanup service.

`python conduit/run.py`

**Cleanup service:**
* Monitors for which messages have been relayed to all servers and purges them from the database.

`python conduit/cleanup.py`

**Running instances manually:**
`python conduit/ircbot.py "<id>" "<host>" "<port>" "<nick>" "<#channel>" "<owner>" "<ssl[1/0]>"`

#### COMMANDS:

```
- Invite 
Access: bot owner(s)
Command: !invite <nick!username@hostmask> <rank> <network>
Ranks: 0 (banned), 1 (member), 10 (halfop), 100 (op)

- Join 
Access: users with a rank above 0
Command: !join <channel>

- Users 
Access: users with a rank above 0
Command: !users <channel>
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