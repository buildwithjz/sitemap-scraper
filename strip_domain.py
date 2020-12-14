# Will remove the http(s):// and everything after the first /
# e.g. https://www.google.com/maps becomes www.google.com
def strip_domain(domain):
    return domain.split('://')[1].split('/')[0]