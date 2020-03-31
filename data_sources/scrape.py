import urllib
import urllib.request
from bs4 import BeautifulSoup
import sys
import re
import requests

#url_source = "http://maynard.patriotproperties.com/search-middle-ns.asp?SearchBuildingType=APRTMNT+CONV"
#url_source = "http://maynard.patriotproperties.com/SearchResults.asp?SearchBuildingType=APRTMNT+CONV"
url_source = "http://maynard.patriotproperties.com/SearchResults.asp?SearchLUC=111&SearchLUCDescription=4-8-UNIT-APT&SearchSubmitted=yes"
base_url = "http://maynard.patriotproperties.com"
summary_bottom_url = "http://maynard.patriotproperties.com/summary-bottom.asp"


#SearchParcel=&SearchBuildingType=&SearchLotSize=&SearchLotSizeThru=&SearchTotalValue=&SearchTotalValueThru=&SearchOwner=&SearchYearBuilt=&SearchYearBuiltThru=&SearchFinSize=&SearchFinSizeThru=&SearchSalePrice=&SearchSalePriceThru=&SearchStreetName=&SearchBedrooms=&SearchBedroomsThru=&SearchNeighborhood=&SearchNBHDescription=&SearchSaleDate=&SearchSaleDateThru=&SearchStreetNumber=&SearchBathrooms=&SearchBathroomsThru=&SearchLUC=111&SearchLUCDescription=4-8-UNIT-APT&SearchBook=&SearchPage=&SearchSubmitted=yes&cmdGo=Go

TAG_RE = re.compile(r'<[^>]+>')
cookies = None


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
    text = re.sub("\\s+", " ", text)
    return TAG_RE.sub('', text)


def get_summary_url(html):
    html = html.lower()
    mo = re.search('href="(.*?)"', html)
    if mo:
        return "{}/{}".format(base_url, mo.group(1))
    else:
        return None


def find_total_pages(html):
    mo = re.search(">Print page .*? of (.*?)<", html)
    if mo:
        page_num = int(mo.group(1))
        return page_num
    else:
        raise Exception("Cant find page number in html source")


def get_summary_page_details(summary_url):
    global cookies

    if summary_url is None:
        return {}
    data = {}
    obj = requests.get(summary_url, cookies=cookies)
    #print(summary_url)
    #print(obj.headers)
    if obj.cookies:
        print(obj.cookies)
        cookies = obj.cookies

    obj = requests.get(summary_bottom_url, cookies=cookies)
    html = obj.text

    if obj.cookies:
        print(obj.cookies)
        cookies = obj.cookies
    #html = str(urllib.request.urlopen(summary_url).read()).lower()

    print(html)
    mo = re.findall("(<table.*?</table>)", html, flags=re.MULTILINE|re.DOTALL)
    #print(mo)


def get_data():
    global cookies
    pages = []
    
    page_number = 1
    while True:
        page_url = "{}&page={}".format(url_source, str(page_number))
        print(page_url)
        obj = requests.get(page_url, cookies=cookies)
        result = obj.text
        #print("headers", obj.headers)
        #print("cookies", obj.cookies)
        if obj.cookies:
            cookies = obj.cookies
            print(obj.cookies)
        #result = str(urllib.request.urlopen(page_url).read())

        yield result

        total_pages = find_total_pages(result)
        if page_number == total_pages:
            return pages

        page_number += 1
    

def parse_html_records_page(html):
    records = []
    html = str(html).lower()
    mo = re.search("<tbody>(.*)</tbody>", str(html), flags=re.MULTILINE|re.DOTALL)
    tdata = mo.group(0)
    results = re.findall("<tr.*?</tr>", tdata, flags=re.MULTILINE|re.DOTALL)

    for i, tr in enumerate(results):
        data = {}
        tds = re.findall("<td.*?</td>", tr, flags=re.MULTILINE|re.DOTALL)
        
        data["summary_url"] = get_summary_url(tds[0])
        summary_details = get_summary_page_details(data["summary_url"])
        data["parcel_id"] = remove_tags(tds[0])
        data["address"] = remove_tags(tds[1])
        data["owner"] = remove_tags(tds[2])
        built_type_list = remove_tags(tds[3].split("<br>"))
        data["built"] = built_type_list[0]
        data["type"] = built_type_list[1:]
        data["total_value"] = remove_tags(tds[4])
        data["beds"], data["baths"] = remove_tags(tds[5].split("<br>"))
        data["lot_size"], data["finish_area"] = remove_tags(tds[6].split("<br>"))
        data["luc"], data["desc"] = remove_tags(tds[7].split("<br>"))
        data["zone"] = remove_tags(tds[8])
        data["dale_date"], data["sale_price"] = remove_tags(tds[9].split("<br>"))
        data["book_page"] = remove_tags(tds[10])
        records.append(data)
    return records

    
def main():
    records = []
    for page in get_data():
        r = parse_html_records_page(page)
        records.extend(r)
        print("records = {}  total records = {}".format(len(r), len(records)))


if __name__ == "__main__":
    main()
