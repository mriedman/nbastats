<h1>NBA Stats finder</h1>
Welcome to my NBA Stats finder! This is a collection of projects I've built up
over the years to investigate NBA statistics of all sorts.
The codebase is currently split into the following four folders:
<ul>
    <li>
    <h4>core</h4>
    This contains files necessary to scrape <a href="basketball-reference.com">BBREF</a>. To download and create the compressed files used by the other programs for the 2021 season, run projects/maketeam.py
    </li>
    <li>
    <h4>nbacom</h4>
    Here, I include files I used to run a clustering analysis to classify players on offense based on their play-type frequencies 
    and on defense based on the types of offensive players they guarded. (For example, players who always guard the other team's star 
    guard get grouped together). Some fun insights (all in the 2020-21 season):
    <ul>
        <li>In one run of K-Means  with 9 groups on offense, a group of 6 players emerged: Zion Williamson, Giannis Antetokounmpo, Bam Adebayo, Bruce Brown...and James Wiseman. What will this mean for the Warriors this year?</li>
        <li>Players don't always play the same position on offense and defense. For example, James Harden's offensive game gets
        grouped with players like Steph Curry, Trae Young, and Tyler Herro, but on defense, he's closer to big men like
        Grant Williams and Pascal Siakam, reflecting his teams' tendency to leverage his size and strength</li>
        <li>This tool is NOT meant to determine how good a player is, only their playstyle. If Andre Drummond shot 10 threes per game next year,
        he'd be grouped with players like Steph Curry, but their impacts couldn't be more different.</li>
    </ul>
    </li>
    <li><h4>player_rate</h4>
    Here, I use a regression analysis on all 10-man lineups (5 for each team) to determine the value of each player on 
    offense and defense as measured in points added per 100 possessions. Honestly, there aren't many surprises here.
    When I simulate fake lineup data to reflect my assumptions (namely, that the players add what I think they do and 
    that impact scales linearly), the regression score stays the same. When I add in lineup type data from nbacom,
    the regression score only marginally increases, suggesting no frequently-used payer type combo is helping or hurting
    performance.</li>
    <li><h4>projects</h4>Just a few random, minor things to answer questions I was curious about!</li></li>
</ul>