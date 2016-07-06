# Swiss-Tournament-Pairings
[IPND] Stage 5 Elective: Back-End Path Project (Tournament Results)

## Stage 5 Details

I developed a database schema to store the game matches between players. I then wrote code to query this data and determine the winners of various games. Additional features bryond the basic rubrics were also developed.

## Setup

- Install [Vagrant](https://www.vagrantup.com/downloads.html) and [Virtualbox](https://www.virtualbox.org/wiki/Downloads)
- Choose any directory and create folder named `vagrant`
- Create folder `tournament` within `vagrant` 
- Navigate to vagrant folder with command line and run:
```
vagrant up
vagrant ssh
cd /vagrant/tournament
psql
\i tournament.sql 
```
- Enter `psql` to access PostgreSQL command line
- Then import `tournament.sql` to set up database and tables
```
vagrant@vagrant-ubuntu-trusty-32:/vagrant/tournament$ psql
vagrant=> \i tournament.sql
tournament=> \q
```

Then run the test
```
vagrant@vagrant-ubuntu-trusty-32:/vagrant/tournament$ python tournament_test.py
```
## Additions Beyond Rubric Objectives
- Support more than one tournament in the database, so matches do not have to be deleted between tournaments.
- Prevent rematches between players.
- Does not assume an even number of players. If there is an odd number of players, one player will be assigned a "bye" (skipped round). A bye counts as a free win. A player will not receive more than one bye in a tournament.
- Support games where a draw (tied game) is possible.
- When two players have the same number of wins, they will be ranked according to OMW (Opponent Match Wins), the total number of wins by players they have played against.
