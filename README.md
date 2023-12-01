# BSC-Scan
Scrape token transaction using token url from bsc scan

# How to setup on local

**Step 1 :** First of all download the zip or clone the repo.

**Step 2 :** Unzip the file that you have downloaded from above step

**Step 3 :** Add the local path under the ‘ **config.ini** ’ file like this if file not present make ‘ **config.ini** ’ file:

        [give name as you like]
                sender_mail = <xxxx@gmail.com>        
                sender_pass = <xxxxxx>
                server = <smtp.gmail.com:587 or server you have>
                recevier_email = <xxxx@gmail.com>

**Step 4 :** Change ' **env = 'DEVELOPMENT'** ' in main.py as per the section name you given in config file.
