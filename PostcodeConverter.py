from bs4 import BeautifulSoup
import urllib.request
import re


class PostcodeConverter():
    
    def __init__(self):
        self.regex_latlong = r'(?:=)(.*?)(?:%2C)(.*?)(?:&)'
    
    def get_soup(self, url):
        """
        This function scrapes given url
        Retrieves the result as soup
        """
        # Perform the request
        request = urllib.request.Request(url)

        # Set a normal User Agent header, otherwise Google will block the request.
        request.add_header('User-Agent',\
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML,\
                    like Gecko) Chrome/87.0.4280.88 Safari/537.36')
        raw_response = urllib.request.urlopen(request).read()

        # Read the repsonse as a utf-8 string
        html = raw_response.decode("utf-8")

        # The code to get the html contents here.

        return BeautifulSoup(html, 'html.parser')

    def get_lat_long(self, soup):

        """
        returns lat long as a tuple 
        """

        str_to_parse = soup.find('meta', {'itemprop': 'image'}).get('content')

        return re.findall(self.regex_latlong, str_to_parse)[0]

    def convert_postcode_to_lat_long(self, postcode, city):
        #https://www.google.com/maps/place/02-516+Warsaw

        url = f"https://www.google.com/maps/place/{postcode.replace(' ', '+')}+{city.replace(' ', '+')}"

        soup = self.get_soup(url)

        lat, long = self.get_lat_long(soup)

        return lat, long

        


# post_code_converter = PostcodeConverter()


# test_data = [('6224eh', 'maastricht'), ('02-516', 'warsaw'), ('10005','new york')]

# for postcode, city in test_data:

#     lat, long = post_code_converter.convert_postcode_to_lat_long(postcode, city)

#     print(f'For the city of {city.title()} and postcode: {postcode}')
#     print (f'This is fucking lat {lat}\nThis is fucking long {long}')
#     print(f'-'*50)