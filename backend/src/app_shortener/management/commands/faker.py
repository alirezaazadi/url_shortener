import datetime
import random
import uuid

from app_shortener.models import URLMap, History
from app_shortener.utilities import random_date, generate_random_string
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.utils.timezone import now, make_aware

User = get_user_model()

RANDOM_STRING_LENGTH = 10
USER_COUNT = 100
URL_COUNT = 100
DAYS_AGO = 80


def generate_url(count):
    user_pks = list(User.objects.all().order_by('?').values_list('pk', flat=True)[:USER_COUNT])
    buffer = list()
    for _ in range(count):
        original_string = str(uuid.uuid1())

        buffer.append(URLMap(
            user_id=random.choice(user_pks),
            short_url=generate_random_string(original_string=original_string),
            original_url=original_string,
        ))

        if len(buffer) == 1000:
            URLMap.objects.bulk_create(buffer, batch_size=1000)
            buffer.clear()

    if buffer:
        URLMap.objects.bulk_create(buffer, batch_size=len(buffer))


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-c', type=int, default=10_000_000, help='count of fake data')
        parser.add_argument('-s', type=bool, default=False, help='create only fake histories')

    @staticmethod
    def _generate_in_bulk(model, instance_generator, count, buffer_size=1000, batch_size=1000):
        buffer = list()
        for _ in range(count):
            try:
                instance = next(instance_generator)
            except StopIteration:
                pass
            else:
                buffer.append(instance)
            if len(buffer) == buffer_size:
                model._meta.default_manager.bulk_create(buffer, batch_size=batch_size)  # noqa
                buffer.clear()
        if buffer:
            model._meta.default_manager.bulk_create(buffer, batch_size=batch_size)  # noqa

    def generate_user(self, count=USER_COUNT):
        from django.utils.crypto import get_random_string

        users = [(get_random_string(length=RANDOM_STRING_LENGTH),
                  f'{get_random_string(length=RANDOM_STRING_LENGTH)}@gmail.com') for _ in range(count)]

        def instance_callback():
            for _ in range(count):
                user = users.pop()
                yield User(
                    username=user[0],
                    email=user[1],
                )

        self._generate_in_bulk(User, instance_callback(), count)

    def generate_history(self, count):
        if URLMap.objects.count() < URL_COUNT:
            self.stdout.write(self.style.SUCCESS('Generating URLS'))
            generate_url(URL_COUNT)
            self.stdout.write(self.style.SUCCESS('URLS DONE'))

        url_pks = URLMap.objects.all().order_by('?').values_list('pk', flat=True)[:URL_COUNT]
        user_pks = User.objects.all().order_by('?').values_list('pk', flat=True)[:USER_COUNT]

        date_range = [now() - datetime.timedelta(days=DAYS_AGO),
                      make_aware(datetime.datetime.combine(now().date(), datetime.time.max))]

        browsers = (
            'IE Mobile',
            'Opera Mobile',
            'Opera Mini',
            'Chrome Mobile',
            'Chrome Mobile WebView',
            'Chrome Mobile iOS',
        )

        def instance_callback():
            for _ in range(count):
                yield History(
                    user_id=random.choice(user_pks),
                    url_id=random.choice(url_pks),
                    created_at=make_aware(random_date(*date_range)),
                    platform=random.choice(History.Platform.choices)[0],
                    browser=random.choice(browsers)
                )

        self._generate_in_bulk(History, instance_callback(), count)

    def handle(self, *args, **options):
        count = options['c']
        history = options['s']

        if User.objects.count() < USER_COUNT:
            self.generate_user()

        if history:
            self.stdout.write(self.style.WARNING('Generating Statistics'))
            self.generate_history(count)
            self.stdout.write(self.style.SUCCESS('Statistics DONE'))
        else:

            # generating urls

            self.stdout.write(self.style.WARNING('Generating URLS'))
            generate_url(count)
            self.stdout.write(self.style.SUCCESS('URLS DONE'))

            # generating statistics
            self.stdout.write(self.style.WARNING('Generating Statistics'))
            self.generate_history(count)
            self.stdout.write(self.style.SUCCESS('Statistics DONE'))
