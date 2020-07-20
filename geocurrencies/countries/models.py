import os
import pytz
from pytz import timezone
import re
import requests
from datetime import datetime
from pycountry import countries
from countryinfo import CountryInfo

from django.core.cache import cache
from django.conf import settings
from django.db import models


from .helpers import ColorProximity, hextorgb
from .settings import *


class CountryManager(models.Manager):

    def get_by_color(self, color, proximity=1):
        """
        Take a hex color and finds near country based on flag and color proximity
        :param color: hex color (FFF, FFFFFF, FFFFFFFF, #FFF, #FFFFFF, #FFFFFFFF)
        :param proximity: succes rate, positive if below (100 is opposite, 0 is identical
        """
        cp = ColorProximity()
        rgb_color = hextorgb(color)
        countries = []
        for country in Country.objects.filter(colors__isnull=False):
            for fc in country.colors.split(','):
                flag_color = hextorgb(fc)
                if cp.proximity(rgb_color, flag_color) < proximity:
                    countries.append(country.pk)
                    break
        return Country.objects.filter(pk__in=set(countries))


class Country(CountryInfo):
    # data extracted from pycountry as basic data if CountryInfo for this country does not exist
    alpha_2 = None
    alpha_3 = None
    name = None
    numeric = None

    def __init__(self, country_name):
        """
        Init a Country object with an alpha2 code
        :params country_name: ISO-3166 alpha_2 code
        """
        super(Country, self).__init__(country_name)
        for field, value in countries.get(alpha_2=country_name)._fields.items():
            setattr(self, field, value)

    @classmethod
    def all_countries(cls):
        """
        List all countries, instanciate CountryInfo for each country in pycountry.countries
        """
        return list(map(lambda x:cls(x.alpha_2), countries))

    def base(self):
        """
        Returns a basic representation of a country with name and iso codes
        """
        return countries.get(alpha_2=self.alpha_2)._fields

    @property
    def timezones(self):
        output = []
        fmt = '%z'
        base_time = datetime.utcnow()
        for tz_info in pytz.country_timezones[self.alpha_2]:
            tz = timezone(tz_info)
            offset = tz.localize(base_time).strftime(fmt)
            numeric_offset = float(offset[:-2] + '.' + offset[-2:])
            output.append({
                'name': tz_info,
                'offset': f'UTC {offset}',
                'numeric_offset': numeric_offset,
                'current_time': base_time.astimezone(tz).strftime('%Y-%m-%d %H:%M')
            })
        return sorted(output, key=lambda x: x['numeric_offset'])

    @property
    def flag_path(self):
        """
        Path to the flag temporary file
        :return: string, absolute path to the flag file
        """
        return os.path.join(settings.MEDIA_ROOT, self.alpha_2 + '.svg')

    def flag_exists(self):
        """
        Checks if flag file exists
        :return: bool, True if flag exists, False otherwise
        """
        return os.path.exists(self.flag_path)

    def download_flag(self):
        """
        Downloads flag for country in temporary path
        :return: Path to the file
        """
        if not self.flag_exists():
            response = requests.get(FLAG_SOURCE.format(alpha_2=self.alpha_2))
            try:
                flag_content = response.text
                flag_file = open(self.flag_path, 'w')
                flag_file.write(flag_content)
                flag_file.close()
                return self.flag_path
            except IOError:
                print("unable to write file", self.flag_path)
                return None

    def analyze_flag(self):
        """
        Analyze colors of the flag for the country and caches the result
        :returns: array, list of colors
        """
        flag_path = os.path.join(settings.MEDIA_ROOT, self.alpha_2 + '.svg')
        # Checks if flag has been downloaded, downloads it otherwise, and return None if download failed
        if not self.flag_exists() and not self.download_flag():
            return None
        with open(flag_path, 'r') as flag:
            content = flag.read()
            result = re.findall(r'\#[0-9A-Fa-f]{1,2}[0-9A-Fa-f]{1,2}[0-9A-Fa-f]{1,2}', content)
            if result:
                cache.set('COLORS-' + self.alpha_2, result)
            return result

    def colors(self):
        """
        List colors present in the flag of the country
        :returns: array, list of colors
        """
        if colors := cache.get('COLORS-' + self.alpha_2):
            return colors
        else:
            return self.analyze_flag()