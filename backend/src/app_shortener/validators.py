from django.core.validators import RegexValidator


class ShortURLValidation(RegexValidator):
    regex = r'^[\w\d]*$'
    message = 'short url must contain only numbers or letters'


short_url_validator = ShortURLValidation()
