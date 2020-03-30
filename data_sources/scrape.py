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
    if isinstance(text, list):
        return_list = []
        for item in text:
            return_list.append(remove_tags(item))
        return return_list
    text = text.replace("\\n", "")
    text = text.replace("\\r", "")
    text = text.replace("\\t", "")
    text = text.replace("&nbsp;", "")
    text = text.replace("&amp;", "")
    text = re.sub("\s+", " ", text)
    return TAG_RE.sub('', text)


def find_total_pages(html):
    mo = re.search(">Print page .*? of (.*?)<", html)
    if mo:
        page_num = int(mo.group(1))
        return page_num
    else:
        raise("Cant find page number in html source")


def get_data(source):
    pages = []
    
    page_number = 1
    while True:
        page_url = "{}&page={}".format(url_source, str(page_number))
        print(page_url)
        result = str(urllib.request.urlopen(page_url).read())

        #print(type(result), page_url, "\n\n\n\n\n\n"*5)
        print(result)
        pages.append(result)

        total_pages = find_total_pages(result)
        print(total_pages)
        if page_number == total_pages:
            return pages

        page_number += 1
    

def parse_html_data(html):
    data = {}
    html = str(html).lower()
    mo = re.search("<tbody>(.*)</tbody>", str(html), flags=re.MULTILINE|re.DOTALL)
    #print(html)
    #mo = html.find("<tbody>")
    tdata = mo.group(0)
    print(tdata)
    results = re.findall("<tr.*?</tr>", tdata, flags=re.MULTILINE|re.DOTALL)
    
    
    for i, tr in enumerate(results):
        data = {}
        tds = re.findall("<td.*?</td>", tr, flags=re.MULTILINE|re.DOTALL)
        
        data["parcel_id"] = remove_tags(tds[0])
        data["address"] = remove_tags(tds[1])
        data["owner"] = remove_tags(tds[2])
        #print(tds[3])
        data["built"], data["type"] = remove_tags(tds[3].split("<br>"))
        data["total_value"] = remove_tags(tds[4])
        data["beds"], data["baths"] = remove_tags(tds[5].split("<br>"))
        data["lot_size"], data["finish_area"] = remove_tags(tds[6].split("<br>"))
        data["luc"], data["desc"] = remove_tags(tds[7].split("<br>"))
        data["zone"] = remove_tags(tds[8])
        data["dale_date"], data["sale_price"] = remove_tags(tds[9].split("<br>"))
        data["book_page"] = remove_tags(tds[10])
        print(data)

    
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
    html_data_pages = get_data(url_source)
    records = []
    for page in html_data_pages:
        records.extend(parse_html_data(page))

if __name__ == "__main__":
    main()
