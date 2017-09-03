import simplejson as json
from wordcloud import WordCloud, ImageColorGenerator
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag, FreqDist
from datetime import datetime
from random import shuffle
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

#nltk.download('popular') <-- For installing the important modules

POSTS = list(json.loads(open('NUSWhispers.txt').read()).items())
POSTS.sort(key = lambda x: (x[1]['year'],x[1]['month'],x[1]['day']))
STOPWORDS = set(['student','students','Hi','guy','guys','time','people','friend','friends','life','year','place','girl','girls','someone',
                 'something','everything','anything','one','anyone','everyone','day','etc','lot','man','things','thing','way','person','years','NUS'])

for word in stopwords.words('english'):
    STOPWORDS.add(word)

def gen_text_by_time_period(timeStart,timeEnd):
    '''
    Obtain list of nouns based on start and end date
    timeStart / timeEnd = tuple of integer format (YYYY, MM, DD) Eg. (2017,05,20)
    '''
    global POSTS
    posts = POSTS
    result = []
    
    #Filter relevant dates
    print('Gathering data for {} to {}'.format(timeStart,timeEnd))
    timeStart = datetime(*timeStart[0:3])
    timeEnd = datetime(*timeEnd[0:3])
    posts = filter(lambda x: timeStart <= datetime(int(x[1]['year']),int(x[1]['month']),int(x[1]['day'])),posts) #Filter posts that fall after timeStart
    posts = filter(lambda x: timeEnd >= datetime(int(x[1]['year']),int(x[1]['month']),int(x[1]['day'])),posts)
    
    for idx, post in posts:
        text = post['txt']
        # function to test if something is a noun
        is_noun = lambda pos: 'NN' == pos[:2]

        #NLP Stuff
        tokenized = word_tokenize(text)
        nouns = [word for (word, pos) in pos_tag(tokenized) if (is_noun(pos) and (word not in STOPWORDS))]
        result += list(set(nouns))
        
    print('Data extracted!')
    result = ' '.join(result)
    return result

def gen_text_by_month(month,yearStart=None,yearEnd=None):
    '''
    Obtain list of nouns based on month (int) Eg.5,
    with options yearStart (int) and yearEnd (int) Eg.2017
    '''
    MONTHS = {1:(1,31),2:(1,29),3:(1,31),4:(1,30),5:(1,31),6:(1,30),
              7:(1,31),8:(1,31),9:(1,30),10:(1,31),11:(1,30),12:(1,31)}
    start,end = MONTHS[month]
    yearStart = yearStart if yearStart else 2015
    yearEnd = yearEnd if yearEnd else 2017
    result = []
    for i in range(yearStart,yearEnd + 1):
        result += obtain_nouns_by_time_period((i,month,start),(i,month,end))
    result = ' '.join(result)
    return result

def obtain_all():
    return obtain_nouns_by_time_period((2015,4,7),(2017,9,3))

#freq1 = FreqDist(RESULT) <-- to get word frequency

def generate_save_word_cloud(text,output):
    coloring = np.array(Image.open("BG.jpg")) #<-- Change to desired back ground
    image_colors = ImageColorGenerator(coloring)
    wordcloud = WordCloud(width=2000, height = 1000, color_func=image_colors, mask=coloring).generate(text) #<-- Change mask if you want
    plt.figure(figsize=(20,10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig(output,bbox_inches='tight',pad_inches = 0)
    print('Word cloud saved!')
    return


#Generate word clouds!
#FOC Saga
text = gen_text_by_time_period((2016,6,1),(2016,7,30))
generate_save_word_cloud(text,'FOC.png')

#Summer break
text = ''
for i in range(2014,2018):
    text += gen_text_by_time_period((i,5,8),(i,8,8)) #Agaration
generate_save_word_cloud(text,'summer.png')

#Finals period
text = ''
for i in range(2014,2018):
    text += gen_text_by_time_period((i,11,15),(i,12,8)) #Sem 1 finals period (and a few wks before)
    text += gen_text_by_time_period((i,4,13),(i,5,8)) #Sem 2 finals period (and a few wks before)
generate_save_word_cloud(text,'finals.png')

#Complaining about bus
text = ''
text += gen_text_by_time_period((2017,8,20),(2017,9,3))
generate_save_word_cloud(text,'bus.png')
