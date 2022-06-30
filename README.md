# RSS-Feed-Filter
 Google News RSS Feed Filter

This Google News RSS Feed Filter connects to the website's RSS feed, filters for news items per user's preference (set in triggers.txt), automatically polls the news on a timer (default 2 minutes).

* Save all files in this repo in the same folder

* To edit news filters, please make changes on 'triggers.txt' file

* Rules to change filters in 'triggers.txt':

    - Each line in this file does one of the following:
        ● is blank
        ● is a comment (begins with ​//​ with no spaces preceding the ​//​)
        ● defines a named trigger
        ● adds triggers to the trigger list
    
    - Each type of line is described below.

        ● **Blank**:​ blank lines are ignored. A line that consists only of whitespace is a blank line. 

        ● **Comments**:​ Any line that begins with ​//​ is ignored.

        ● **Trigger definitions**:​ Lines that do not begin with the keyword ADD define named triggers. Elements in these lines are separated by ​**commas​**. The first element in a trigger definition is either the keyword ADD or the name of the trigger. The name can be any combination of letters/numbers, but it cannot be the word "ADD". The second element of a trigger definition is a keyword (e.g., TITLE, AND, etc.) that specifies the type of trigger being defined. The remaining elements of the definition are the trigger arguments. 

        ● What arguments are required depends on the trigger type:
            ● **TITLE​**: one phrase
            ● **DESCRIPTION**​: one phrase
            ● **AFTER​**: one correctly formatted time string
            ● **BEFORE**​: one correctly formatted time string
            ● **NOT​**: the name of the trigger that will be NOT'd
            ● **AND**​: the names of the two triggers that will be AND'd.
            ● **OR**​: the names of the two triggers that will be OR'd.

        ● **Trigger addition**:​ A trigger definition should create a trigger and associate it with a name but should NOT automatically add that trigger to the trigger list. One or more ADD lines in the trigger configuration file will specify which triggers should be in the trigger list. An ADD line begins with the ADD keyword. The elements following ADD are the names of one or more previously defined triggers. The elements in these lines are also separated by commas. These triggers will be added to the the trigger list.



This project is created as the assignment fro problem set 5 of MIT's 6.0001 course "Introduction to Computer Science and Programming in Python" for Fall 2016 term.

The open course can be found here: https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/
