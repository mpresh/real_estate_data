import urllib
import urllib.request
from bs4 import BeautifulSoup
import sys
import re

#url_source = "http://maynard.patriotproperties.com/search-middle-ns.asp?SearchBuildingType=APRTMNT+CONV"
#url_source = "http://maynard.patriotproperties.com/SearchResults.asp?SearchBuildingType=APRTMNT+CONV"
url_source = "http://maynard.patriotproperties.com/SearchResults.asp?SearchLUC=111&SearchLUCDescription=4-8-UNIT-APT"

TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    text = text.replace("\\n", "")
    text = text.replace("\\r", "")
    text = text.replace("\\t", "")
    text = text.replace("&nbsp;", "")
    text = text.replace("&amp;", "")
    text = re.sub("\s+", " ", text)
    return TAG_RE.sub('', text)

def get_data(source):
    result = urllib.request.urlopen(url_source).read()
    return result 

def parse_html_data(html):
    html = str(html).lower()
    mo = re.search("<tbody>(.*)</tbody>", str(html), flags=re.MULTILINE|re.DOTALL)
    #print(html)
    #mo = html.find("<tbody>")
    tdata = mo.group(0)
    print(tdata)
    results = re.findall("<tr.*?</tr>", tdata, flags=re.MULTILINE|re.DOTALL)
    
    
    for i, tr in enumerate(results):
        tds = re.findall("<td.*?</td>", tr, flags=re.MULTILINE|re.DOTALL)
        
        print(remove_tags(tds[0]))
        print(remove_tags(tds[1]))
        print(remove_tags(tds[2]))
        #print(tds[3])
        print(remove_tags(tds[3]))
        print(len(tds))

    
    #soup = BeautifulSoup(html, 'html.parser')

    #s = soup.body.find_all("td")
    #print(len(s))
    #s = list(s.children)
    #print(len(s))
    #for r in s.find_all("tr"):
    #for i, r in enumerate(s):
    #    print(i, r)
    #    print(type(r))
    #print(dir(s))
    #print(type(s))
    #for r in  soup.find(id="T1").find("tbody").find_all("TR"):
    #    print(r)
    #print(soup.prettify())
    #for link in soup.find_all('a'):
    #    print(link.get('href'))

def main():
    html_data = get_data(url_source)
    parse_html_data(html_data)

if __name__ == "__main__":
    main()
