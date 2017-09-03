import json
import datetime
import csv
import time
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request

app_id = "" #Create your own FB app
app_secret = "" #Your FB app_secret
page_id = "695707917166339" #NUSWhispers page

# input date formatted as YYYY-MM-DD
since_date = "2015-04-07"
until_date = "2017-09-04"

access_token = app_id + "|" + app_secret


def request_until_succeed(url):
    req = Request(url)
    success = False
    while success is False:
        try:
            response = urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception as e:
            print(e)
            time.sleep(5)

            print("Error for URL {}: {}".format(url, datetime.datetime.now()))
            print("Retrying.")

    return response.read()


# Needed to write tricky unicode correctly to csv
def unicode_decode(text):
    try:
        return text.encode('utf-8').decode()
    except UnicodeDecodeError:
        return text.encode('utf-8')


def getFacebookPageFeedUrl(base_url):

    # Construct the URL string; see http://stackoverflow.com/a/37239851 for
    # Reactions parameters
    fields = "&fields=message,link,created_time,type,name,id," + \
        "comments.limit(0).summary(true),shares,reactions" + \
        ".limit(0).summary(true)"

    return base_url + fields

def processFacebookPageFeedStatus(status):

    # The status is now a Python dictionary, so for top-level items,
    # we can simply call the key.

    # Additionally, some items may not always exist,
    # so must check for existence first

    status_id = status['id']
    status_type = status['type']

    status_message = '' if 'message' not in status else \
        unicode_decode(status['message'])
    link_name = '' if 'name' not in status else \
        unicode_decode(status['name'])
    status_link = '' if 'link' not in status else \
        unicode_decode(status['link'])

    # Time needs special care since a) it's in UTC and
    # b) it's not easy to use in statistical programs.

    status_published = datetime.datetime.strptime(
        status['created_time'], '%Y-%m-%dT%H:%M:%S+0000')
    status_published = status_published + \
        datetime.timedelta(hours=-5)  # EST
    status_published = status_published.strftime(
        '%Y-%m-%d %H:%M:%S')  # best time format for spreadsheet programs

    # Nested items require chaining dictionary keys.

    num_reactions = 0 if 'reactions' not in status else \
        status['reactions']['summary']['total_count']
    num_comments = 0 if 'comments' not in status else \
        status['comments']['summary']['total_count']
    num_shares = 0 if 'shares' not in status else status['shares']['count']

    return (status_id, status_message, link_name, status_type, status_link,
            status_published, num_reactions, num_comments, num_shares)


def scrapeFacebookPageFeedStatus(page_id, access_token, since_date, until_date):
    #TO STORE THE MESSAGES IN
    #Dictionary with format post_proc_num:{year: 'YYYY' (str), 'month': 'MM' (str) , 'day': 'DD' (str), txt: post_message)
    RESULT = {}
    
    has_next_page = True
    num_processed = 0
    scrape_starttime = datetime.datetime.now()
    after = ''
    base = "https://graph.facebook.com/v2.9"
    node = "/{}/posts".format(page_id)
    parameters = "/?limit={}&access_token={}".format(100, access_token)
    since = "&since={}".format(since_date) if since_date \
        is not '' else ''
    until = "&until={}".format(until_date) if until_date \
        is not '' else ''

    print("Scraping {} Facebook Page: {}\n".format(page_id, scrape_starttime))

    while has_next_page:
        after = '' if after is '' else "&after={}".format(after)
        base_url = base + node + parameters + after + since + until

        url = getFacebookPageFeedUrl(base_url)
        statuses = json.loads(request_until_succeed(url).decode("utf-8"))
        
        for status in statuses['data']:
            try:
                #Remove the URL link from the message
                txt = status['message']
                num = txt.rfind('http')
                txt = txt[0:num-7]

                #Split date into year, month, day
                date = status
                #Store info accordingly
                RESULT[num_processed] = {'year':status['created_time'][0:4],
                                         'month':status['created_time'][5:7],
                                         'day':status['created_time'][8:10],
                                         'txt':txt}
            except KeyError:
                #Some statuses have no message
                continue
            num_processed += 1
            if num_processed % 100 == 0:
                print("{} Statuses Processed: {}".format
                      (num_processed, datetime.datetime.now()))

        # if there is no next page, we're done.
        if 'paging' in statuses:
            after = statuses['paging']['cursors']['after']
        else:
            has_next_page = False

    print("\nDone!\n{} Statuses Processed in {}".format(
        num_processed, datetime.datetime.now() - scrape_starttime))

    #SAVE RESULT TO CSV FILE
    with open('NUSWhispers.txt','w') as outfile:
        json.dump(RESULT,outfile)
    
if __name__ == '__main__':
    scrapeFacebookPageFeedStatus(page_id, access_token, since_date, until_date)
