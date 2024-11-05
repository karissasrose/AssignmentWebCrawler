import re
# ///////////////////////////////////////////////////////////////////////////////////
#                               MY IMPORTS
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from io import StringIO
import pickle
import os
# ///////////////////////////////////////////////////////////////////////////////////


             

STOP_WORDS = set([
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for",
    "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's",
    "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm",
    "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't",
    "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's",
    "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until",
    "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when",
    "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"
])

BAD_SITES = set(['http://www.ics.uci.edu/~cs224','http://www.cert.ics.uci.edu/seminar/Nanda'])

# ///////////////////////////////////////////////////////////////////////////////////
#                              NOTES 
# FINDING THE SUBDOMAINS, I WAS NOT SURE HOW TO DO THAT UNTIL I REALIZED THAT 
# THE QUESTION ITSELF IS THE HINT: HOW MANY SUBDOMIANS DID WE FIND IN THE UCI.EDU DOMAIN?
# THAT WOULD BE CONSIDERED THE KEY, WE NEED TO USE A MAP
# PSEUDOCODE: 
# IF UNDER UCI.EDU DOMAIN: 
# STORE THE SUBDOMIAN AS THE KEY {KEY, NUM_OF_UNIQUE_PAGES}
# THIS SHOULD WORK BECAUSE WE ONLY ENTER THIS IF CONDITION IF WE ARE A SUBDOMAIN OF UCI.EDU 
# APPARENTLY NETLOC CAN HELP US HERE
# ///////////////////////////////////////////////////////////////////////////////////




def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def add_subdomains(url):
    parsed = urlparse(url)
    # # ///////////////////////////////////////////////////////////////////////////////////
    # I WAS WONDERING WHAT NETLOC DID, DID NOT FULL GRASP IT UNTI NOW
    # https://stackoverflow.com/questions/53992694/what-does-netloc-mean
    # ///////////////////////////////////////////////////////////////////////////////////
    pickle_file = 'subdomains.pkl'
    if not os.path.exists(pickle_file):
        subdomains = dict()
    else:
        with open(pickle_file, "rb") as file:
            subdomains = pickle.load(file)
    domain = parsed.netloc.lower()
    if domain.endswith("uci.edu"):
        if domain not in subdomains:
            subdomains[domain] = set()
        subdomains[domain].add(url)
    # PER ASSIGNMENT, SORT
    sorted_subdomains = dict(sorted(subdomains.items()))

    file_path = 'subdomains.txt'
    with open(file_path, "a+") as file:
        file.seek(0)
        file.truncate()
        total_unique_pages = 0
        for subdomain, urls in sorted_subdomains.items():
            # COUNTING UNIQUE SUBDOMAINS
            count = len(urls)
            total_unique_pages += count
            # REQUIRED FORMAT PER ASSIGNMENT
            file.write(f"{subdomain}: \t{count} unique pages\n")
        file.write(f"\n{total_unique_pages} total pages\n")

    temp_pickle_file = 'subdomains.pkl.tmp'
    with open(temp_pickle_file, "wb") as file:
        pickle.dump(sorted_subdomains, file)
    os.replace(temp_pickle_file, pickle_file)

# ///////////////////////////////////////////////////////////////////////////////////
#  I DON'T KNOW WHERE TO WRITE THIS AND BECAUSE WE CAN'T PRINT TO CONSOLE, I WILL WRITE 
#  TO FILE
# ///////////////////////////////////////////////////////////////////////////////////


def tokenize(text):
    file = StringIO(text)
    currentWord = ''
    tokens = []
    while True:
        char = file.read(1)
        if not char: #stop looping if file ended
            if currentWord != '': #if anything left in currentWord, that's a token
                tokens.append(currentWord)
            break
        if not char.isalnum(): #if char is not alphanumeric, it is a separator
            if currentWord != '': #make sure some sort of word was made
                tokens.append(currentWord)
                currentWord = ''
        else: #still reading letters
            currentWord += char.lower()
    file.close()
    return tokens #return tokens found

def computeWordFrequencies(tokens, counts):
    for token in tokens:
        if token in STOP_WORDS:
            pass
        elif token not in counts:
            counts.update({token: 1})
        else:
            counts[token] += 1

def update_longest_page(tokens, url):
    number_of_words = len(tokens)
    #save len of tokenize to file if higher than what's already there
    file_path = 'longest_page.txt'
    with open(file_path, "a+") as file:
        file.seek(0)
        content = file.readlines()
        if not content: #if the file was empty
            file.write(f"{number_of_words}\n{url}")
        else: #there was something in the file
            highest_count = int(content[0])
            if(highest_count < number_of_words):
                file.seek(0)
                file.truncate()
                file.write(f"{number_of_words}\n{url}")


    ########################
    pickle_file = 'freq.pkl'
    if not os.path.exists(pickle_file):
        counts = dict()
    else:
        with open(pickle_file, "rb") as file:
            counts = pickle.load(file)
    computeWordFrequencies(tokens, counts)
    # PER ASSIGNMENT, SORT
    counts = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True)) #TODO: MOVE THIS TO END

    file_path = 'freq.txt'
    with open(file_path, "a+") as file:
        file.seek(0)
        file.truncate()
        for word, cnt in counts.items():
            # REQUIRED FORMAT PER ASSIGNMENT
            file.write(f"{word}: \t{cnt}\n")

    temp_pickle_file = 'freq.pkl.tmp'
    with open(temp_pickle_file, "wb") as file:
        pickle.dump(counts, file)
    os.replace(temp_pickle_file, pickle_file)

    

#New Should be self explanatory basically strips and counts words and makes exception for directories
def low_txt_check(text,url,min_words=100):
    word_count = len(text)
    return word_count < min_words


def check_meta_tags(soup):
    return any(
        (meta.get('name') == 'robots' or meta.get('name') == 'robot') and meta.get('content') is not None and ('noindex' in meta.get('content').lower()  or 'nofollow' in meta.get('content').lower())
        for meta in soup.find_all('meta'))


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    # ///////////////////////////////////////////////////////////////////////////////////
    # PER INSTRUCTIONS, WE NEED TO FIND A WAY TO DETECT DEAD URLS THTA RETURN 200 WHICH IS 
    # THE STATUS-OK NUMBER. THAT BEING SAID, WE SHOULD DO AN EARLY RETURN THAT IS
    # WE CHECK IF THAT STATUS CODE IS 200 I.E OK AND CONTINUE 
    # EDGE CASE? WHAT DO WE RETURN IF NOT A VALID STATUS CODE? FOR NOW I RETURN AN EMPTY LIST
    # ///////////////////////////////////////////////////////////////////////////////////

    if resp.status != 200: 
        return []

    content_type = resp.raw_response.headers.get('Content-Type')
    if content_type == 'application/pdf':
        return []

    # HINT ON THE HW
    b_soup = BeautifulSoup(resp.raw_response.content, "lxml")

    if check_meta_tags(b_soup):
        return []

    try: 
        text = b_soup.get_text(separator=' ', strip=False).encode('utf-8', errors='ignore').decode('utf-8')
    except:
        return []

    tokens = tokenize(text)
    if low_txt_check(tokens, url):
        return []


    update_longest_page(tokens, url)
    add_subdomains(url)

    

    # THE LIST TO RETURN
    # hyperlink now becomaes a set
    hyper_links = set()


    # ///////////////////////////////////////////////////////////////////////////////////
    # BEAUTIFUL SOUP CONTAINS A FIND_ALL FUNCTION BUT HOW DO WE GET HYPERLINKS 
    # I DID NOT KNOW THIS BUT THE <a> TAG IN HTML DEFINES A HYPERLINK
    # https://www.w3schools.com/html/html_links.asp
    # ///////////////////////////////////////////////////////////////////////////////////


    # ///////////////////////////////////////////////////////////////////////////////////
    # DEFINING MY VARIABLE WHAT I WILL LOOP THROUGH SINCE FIND_ALL FROM BEAUTIFUL SOUP FINDS ALL <a> TAGS
    # BEAUTIFULSOUP DOCUMENTAION: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    a_tag = b_soup.find_all("a", href = True)
    # ///////////////////////////////////////////////////////////////////////////////////

    # ///////////////////////////////////////////////////////////////////////////////////
    # THE INSTRUCTIONS SAY, ANY LIBRAIRES THAT MAKE OUR LIVES EASY BUT URLLIB.PARSE HAS OTHER FUNCTIONS 
    # THAT WOULD MAKE OUR LIVES EASIER. FUNNY ENOUGH, I DOUBT ANYONE WILL READ THIS BUT PROFESSORS 
    # LOVE TO IMPORT PARTIALLY AND ITS UP TO USE THE STUDENTS TO EXPLORE THOSE LIBRARIES
    # https://docs.python.org/3/library/urllib.parse.html
    # ///////////////////////////////////////////////////////////////////////////////////
    for a in a_tag:
        # ///////////////////////////////////////////////////////////////////////////////////
        # PER INSTRUCTIONS, RETURN URLS AS A LIST OF STRINGS AND REMOVE FRAGMENT PART
        # ///////////////////////////////////////////////////////////////////////////////////
        link = str(urljoin(url, a['href']).split('#')[0])
        hyper_links.add(link)
    # CONVERTED BACK TO A LIST PER REQUIREMENTS
    return list(hyper_links)



def is_valid(url):
    valid_domains = {
        "ics.uci.edu",
        "cs.uci.edu",
        "informatics.uci.edu",
        "stat.uci.edu",
        "today.uci.edu/department/information_computer_sciences",

    }
    if url in BAD_SITES:
        return False
  
    try:
        parsed = urlparse(url)
        
        # Ensure the scheme is either HTTP or HTTPS
        if parsed.scheme not in {"http", "https"}:
            return False
        
        # Check if netloc is exactly one of the valid domains or a subdomain
        if not any(parsed.netloc == domain or parsed.netloc.endswith("." + domain) for domain in valid_domains):
            return False
        
        if "filter" in url:
            return False
        
        if "sort" in url:
            return False

        path = parsed.path.lower()

        # /////////////////////////////////////////////////////////////////////////////////// 
        # https://docs.python.org/3/library/re.html#re.search
        # search(pattern,string)
        # /////////////////////////////////////////////////////////////////////////////////// 

        #NEW Check for calender and pagination traps which we seem to run into
        if re.search(r"/\d{4}/\d{1,2}/\d{0,2}", parsed.path) or re.search(r"page=\d+" ,parsed.path) or re.search(r"\d{1,2}-\d{1,2}-\d{4}", parsed.path) or re.search(r"\d{4}-\d{1,2}-\d{1,2}", parsed.path) or re.search(r"/\d{0,2}/\d{1,2}/\d{4}", parsed.path):
            return False
    
        if re.search(r"sort=", parsed.query) or re.search(r"filter=", parsed.query):
            return False

        if re.search(r"/(\w+)/\1/", path):
            return False

        # /////////////////////////////////////////////////////////////////////////////////// 
        # PREVIOUS CODE USING IF NOT WAS CONFUSING TO ME, YEAH YEAH, IT IS THE SAME AS THE 
        # BELOW CODE BUT WRITING FEWER LINES OF CODE DOES NOT MAKE THE PROGRAM READABLE 
        # ///////////////////////////////////////////////////////////////////////////////////

        if re.search(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            r"|png|tiff?|mid|mp2|mp3|mp4"
            r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            r"|epub|dll|cnf|tgz|sha1"
            r"|thmx|mso|arff|rtf|jar|csv"
            r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            return False
        
     
        return True

    except TypeError:
        print("TypeError for ", parsed)
        raise