from bs4 import BeautifulSoup
import pandas as pd
import requests

catalog_export = pd.read_csv("catalog-export.csv")
catalog_export = catalog_export[(catalog_export["visibility"] == "Catalog, Search")]
urls = catalog_export["url_key"]
headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}
page_data = pd.DataFrame()
spec_columns = []

def make_req(url):
  url = str(url)
  site = requests.get("https://matsinc.com/" + url, headers=headers)
  if (site.status_code != 200):
    site = requests.get("https://matsinc.com/" + url + ".html", headers=headers)
    if (site.status_code != 200):
      return False
    else:
      return site
  else:
    return site

def make_soup(doc):
  site = make_req(doc)
  if (site):
    soup = BeautifulSoup(site.content, "lxml")
    return soup
  else:
    return False

# loppy
for doc in urls:
  raw_doc = make_soup(doc)
  
  if (raw_doc):
    title = raw_doc.find('title')
    title = title.text

    h1 = raw_doc.find(itemprop="name")
    h1 = h1.text

    sku = raw_doc.find(itemprop="sku")
    sku = sku.text

    # why is it faster to do it this way?!? gross.
    description = raw_doc.find(itemprop="description")
    description = description.text
    description = description.strip()
    
    all_specs = raw_doc.find_all('div', class_="col-sm-12 col-lg-4 columns")
    
    for spec in all_specs:
      spec_texts = spec.find_all('p')

      for text in spec_texts:
        spec_title = text.find('span')
        parse_text = text.text

        if (spec_title != None):
          spec_text = parse_text.split(spec_title.text)[1]
          spec_title = spec_title.text.strip()

          if spec_title not in spec_columns:
            spec_columns.append(spec_title)
            page_data[spec_title] = ""
          
          new_spec = {
            "SKU": sku,
            "name": h1,
            "title": title,
            "description": description,
            spec_title: spec_text
          }
        else:
          new_spec = {
            "SKU": sku,
            "name": h1,
            "title": title,
            "description": description,
            "spec-text": parse_text
          }

        page_data = page_data.append(new_spec, ignore_index=True)

  else:
    print(doc + " error in URL")

print(spec_columns)
page_data.to_csv("catalog_scrape.csv", index=False)