
import feedparser
import string
import time
import threading
from project_util import translate_html
from mtTkinter import *
from datetime import datetime
import pytz
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
TRIGGERS_FILENAME = dir_path + "/" + 'triggers.txt'

#-----------------------------------------------------------------------

#======================
# Code for retrieving and parsing
# Google News feeds
#======================

def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory-s.
    """
    feed = feedparser.parse(url)
    entries = feed.entries
    ret = []
    for entry in entries:
        guid = entry.guid
        title = translate_html(entry.title)
        link = entry.link
        description = translate_html(entry.description)
        pubdate = translate_html(entry.published)

        try:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
            pubdate.replace(tzinfo=pytz.timezone("GMT"))
        except ValueError:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %z")

        newsStory = NewsStory(guid, title, description, link, pubdate)
        ret.append(newsStory)
    return ret

#======================
# Data structure design
#======================

class NewsStory(object):
    def __init__(self, guid:str, title:str, description:str, link:str, pubdate):
        self.guid = guid
        self.title = title
        self.description = description
        self.link = link
        self.pubdate = pubdate
    
    def get_guid(self):
        return self.guid
    def get_title(self):
        return self.title
    def get_description(self):
        return self.description
    def get_link(self):
        return self.link
    def get_pubdate(self):
        return self.pubdate


#======================
# Triggers
#======================

class Trigger(object):
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        raise NotImplementedError

# PHRASE TRIGGERS
class PhraseTrigger(Trigger):
    def __init__(self, phrase:str):
        self.phrase = phrase.lower()
    def is_phrase_in(self, text:str):
        # add space before and after string to search for exact match
        search_phrase = ' ' + self.phrase + ' '
        search_in_text = text.lower()
        for sign in string.punctuation:
            search_in_text = search_in_text.replace(sign, ' ')
        # add space before and after in case search_phrase is in begin or end
        search_in_text = ' ' + ' '.join(search_in_text.split()) + ' '
        return search_phrase in search_in_text


class TitleTrigger(PhraseTrigger):
    def __init__(self, phrase: str):
        super().__init__(phrase)

    def evaluate(self, story):
        return self.is_phrase_in(story.get_title())

class DescriptionTrigger(PhraseTrigger):
    def __init__(self, phrase: str):
        super().__init__(phrase)

    def evaluate(self, story):
        return self.is_phrase_in(story.get_description())

# TIME TRIGGERS
class TimeTrigger(Trigger):
# Constructor:
#        Input: Time has to be in EST and in the format of "%d %b %Y %H:%M:%S".
#        Convert time from string to a datetime before saving it as an attribute.
    def __init__(self, time_str:str) -> None:
        '''time_str example: 3 Oct 2016 17:00:10
        '''
        self.day_time = datetime.strptime(time_str, "%d %b %Y %H:%M:%S")

# BeforeTrigger and AfterTrigger
class BeforeTrigger(TimeTrigger):
    def __init__(self, time_str: str) -> None:
        super().__init__(time_str)
    def evaluate(self, story):
        try:
            return story.get_pubdate() < self.day_time
        except TypeError:
            self.day_time = self.day_time.replace(tzinfo=pytz.timezone("EST"))
            return story.get_pubdate() < self.day_time

class AfterTrigger(TimeTrigger):
    def __init__(self, time_str: str) -> None:
        super().__init__(time_str)
    def evaluate(self, story):
        try:
            return story.get_pubdate() > self.day_time
        except TypeError:
            self.day_time = self.day_time.replace(tzinfo=pytz.timezone("EST"))
            return story.get_pubdate() > self.day_time


# COMPOSITE TRIGGERS
class NotTrigger(Trigger):
    def __init__(self, T) -> None:
        self.trigger = T
    def evaluate(self, story):
        return not self.trigger.evaluate(story)

class AndTrigger(Trigger):
    def __init__(self, trigger1, trigger2) -> None:
        self.trigger1 = trigger1
        self.trigger2 = trigger2
    def evaluate(self, story):
        return self.trigger1.evaluate(story) and self.trigger2.evaluate(story)

class OrTrigger(Trigger):
    def __init__(self, trigger1, trigger2) -> None:
        self.trigger1 = trigger1
        self.trigger2 = trigger2
    def evaluate(self, story):
        return self.trigger1.evaluate(story) or self.trigger2.evaluate(story)


#======================
# Filtering
#======================

def filter_stories(stories, triggerlist):
    """
    Takes in a list of NewsStory instances.

    Returns: a list of only the stories for which a trigger in triggerlist fires.
    """
    filtered_stories = []
    for story in stories:
        for trigger in triggerlist:
            if trigger.evaluate(story):
                filtered_stories.append(story)
                break
    
    return filtered_stories



#======================
# User-Specified Triggers
#======================
def read_trigger_config(filename):
    """
    filename: the name of a trigger configuration file

    Returns: a list of trigger objects specified by the trigger configuration
        file.
    """
    trigger_file = open(filename, 'r')
    lines = []
    for line in trigger_file:
        line = line.rstrip()
        if not (len(line) == 0 or line.startswith('//')):
            lines.append(line)

    # trigger even types
    trigger_types = {
        'TITLE'         : TitleTrigger,
        'DESCRIPTION'   : DescriptionTrigger,
        'AFTER'         : AfterTrigger,
        'BEFORE'        : BeforeTrigger,
        'NOT'           : NotTrigger,
        'AND'           : AndTrigger,
        'OR'            : OrTrigger
        }

    # include all trigger events in this dictionary
    all_trigger_dict = {}
    final_trigger_list  = []
    
    # trigger_line in triggers.txt file comes in a format: 
    # trigger_name,trigger_event,trigger_object(s)
    for trigger_line in lines:
        trigger_detail = trigger_line.split(',')
        trigger_name = trigger_detail[0]
        
        # ignore lines starts with 'ADD' 
        # add the trigger event to final trigger list
        if trigger_name == 'ADD': 
            for trigger in trigger_detail[1:]:
                final_trigger_list.append(all_trigger_dict[trigger])
            continue
        
        trigger_event = trigger_detail[1]
        trigger_arg1 = trigger_detail[2]
        # if the trigger name reference already exists in all_trigger_dict
        # should get the actual trigger event instead of the reference name
        trigger_object1 = all_trigger_dict.get(trigger_arg1, trigger_arg1)
        
        # trigger events like TITLE, DESCRIPTION, BEFORE, AFTER, NOT
        if len(trigger_detail) == 3: 
            all_trigger_dict[trigger_name] = trigger_types[trigger_event](trigger_object1)
        # trigger events like AND, OR 
        elif len(trigger_detail) == 4:    
            trigger_arg2 = trigger_detail[3]
            trigger_object2 = all_trigger_dict.get(trigger_arg2, trigger_arg2)
            all_trigger_dict[trigger_name] = trigger_types[trigger_event](trigger_object1, trigger_object2)

    return final_trigger_list


SLEEPTIME = 120 #seconds -- how often we poll

def main_thread(master):
    try:
        triggerlist = read_trigger_config(TRIGGERS_FILENAME)
        
        # Draws the popup window that displays the filtered stories
        # Retrieves and filters the stories from the RSS feeds
        frame = Frame(master)
        frame.pack(side=BOTTOM)
        scrollbar = Scrollbar(master)
        scrollbar.pack(side=RIGHT,fill=Y)

        t = "Google Top News"
        title = StringVar()
        title.set(t)
        ttl = Label(master, textvariable=title, font=("Helvetica", 18))
        ttl.pack(side=TOP)
        cont = Text(master, font=("Helvetica",14), yscrollcommand=scrollbar.set)
        cont.pack(side=BOTTOM)
        cont.tag_config("title", justify='center')
        button = Button(frame, text="Exit", command=root.destroy)
        button.pack(side=BOTTOM)
        guidShown = []
        def get_cont(newstory):
            if newstory.get_guid() not in guidShown:
                cont.insert(END, newstory.get_title()+"\n", "title")
                cont.insert(END, "\n---------------------------------------------------------------\n", "title")
                cont.insert(END, newstory.get_description())
                cont.insert(END, "\n*********************************************************************\n", "title")
                guidShown.append(newstory.get_guid())

        while True:

            print("Polling . . .", end=' ')
            # Get stories from Google's Top Stories RSS news feed
            stories = process("http://news.google.com/news?output=rss")

            stories = filter_stories(stories, triggerlist)

            list(map(get_cont, stories))
            scrollbar.config(command=cont.yview)


            print("Sleeping...")
            time.sleep(SLEEPTIME)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    root = Tk()
    root.title("Some RSS parser")
    t = threading.Thread(target=main_thread, args=(root,))
    t.start()
    root.mainloop()

