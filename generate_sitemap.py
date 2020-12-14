from usp.tree import sitemap_tree_for_homepage
import json
import csv
from os import listdir
from strip_domain import strip_domain

#
# Will generate one file per DOMAIN (not topic)
#

# The sitemap folder will act as the NoSQL 'database' with each domain acting as its own table
SITEMAP_FOLDER = './'

def generate_sitemap(domain):

  # Generate the sitemap
  tree = sitemap_tree_for_homepage(domain)

  # Initialise the list of links
  links = []

  # Iterate through all URLs found by the sitemap generator
  for page in tree.all_pages():
    url = page.url

    # Some sites will not have the domain name in front of URL == add this in
    if url[0] == '/':
      url = domain + url

    # This is the structure of the db
    # Needs work to improve search functionality
    link_entry = {
      'url': url,
      'domain': 'https://'+strip_domain(domain)
    }

    #Add this to the list of links needing to be appended
    links.append(link_entry)
  
  # Write the links to a file (one for each domain) 
  write_to_file(domain, links)


# Write the list of links to a file
def write_to_file(domain, links):

  # Will only put the domain name without protocol and paths to filename
  filename = domain.split('://')[1].split('/')[0] + '.json'

  # Open the file for writing
  with open(SITEMAP_FOLDER + '/' + filename, 'w') as fout:
    json.dump(links, fout)