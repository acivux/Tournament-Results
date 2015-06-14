###Tournament Results

#####Installation
- Download the files from https://github.com/acivux/Tournament-Results
- Copy all the project files into the same folder.

######Setting up the PostgreSQL Database 
Make sure PostgreSQL is  installed and functions. See the [installation](http://www.postgresql.org/docs/9.4/interactive/tutorial-install.html) instructions.

Open the *psql* command line tool, making sure the current working directory is the same directory where this project is saved.

Create a new database called "tournament"

```CREATE DATABASE tournament;``` 

Make the `tournament` database active by using the `\connect` statement:

```\connect tournament```

Set up the tables defined in tournament.sql by using the `\include` statement:

```\include tournament.sql```

The tournament database should now be set up for testing.

######Run the Test 
- Run `tournament_test.py`

##### Requirements
- Python 2.7.6 or later
- This has not been tested on any Apple devices
