import pickle
from datetime import timedelta

from app_shortener.models import URLMap, History
from app_shortener.serializers import CreateShortURLSerializer
from app_shortener.tasks import cache_statistics_in_disk
from app_shortener.utilities import get_date_range, get_n_unit_ago
from django.db.models import Count
from django.http import HttpResponseRedirect, Http404
from django.utils.timezone import now
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response


def _query_builder(url_instance, _range, user_specific):
    if user_specific:
        return History.objects.values('browser', 'platform'). \
            filter(url=url_instance, created_at__range=_range). \
            annotate(Count('user')).order_by()
    else:
        return History.objects.values('browser', 'platform'). \
            filter(url=url_instance, created_at__range=_range). \
            annotate(Count('browser'), Count('platform')).values('platform',
                                                                 'platform__count',
                                                                 'browser',
                                                                 'browser__count')


def _build_response(queryset_result, user_specific, key):
    browsers = {}
    platforms = {}
    total = 0
    for group in queryset_result:
        platform = group['platform']
        browser = group['browser']
        if platform not in platforms:
            temp = group['platform__count'] if not user_specific else group['user__count']
            total += temp
            platforms[platform] = temp
        else:
            temp = group['platform__count'] if not user_specific else group['user__count']
            total += temp
            platforms[platform] += temp

        if browser not in browsers:
            browsers[browser] = group['browser__count'] if not user_specific else group['user__count']
        else:
            browsers[browser] += group['browser__count'] if not user_specific else group['user__count']

    return {
        key: {'browsers': browsers if browsers else None,
              'platforms': platforms if platforms else None,
              'total': total
              }
    }


def _convert_time_frame_to_range(timeframe):
    if timeframe == 1:
        return get_date_range(now())
    else:
        end = get_n_unit_ago(days=1)
        start = get_n_unit_ago(base=end, days=timeframe)
        return [start, end]


def _get_proper_field(timeframe):
    if timeframe == 1:
        return 'current_day_check_date'
    else:
        if timeframe == 30:
            return 'thirty_days_ago_check_date'
        else:
            return 'seven_days_ago_check_date'


def _is_cached(instance, timeframe, key):
    last_check = getattr(instance, _get_proper_field(timeframe))

    if not last_check or key not in instance.cached_statistics:
        return False

    return not (now() - last_check > (timedelta(hours=1) if timeframe == 1 else timedelta(days=1)))


class URLStatisticsAPIView(RetrieveAPIView):
    queryset = URLMap.objects.all()
    permission_classes = [AllowAny]
    lookup_field = 'short_url'

    def get_object(self):
        filter_kwargs = {self.lookup_field: self.kwargs[self.lookup_url_kwarg or self.lookup_field]}
        instance: URLMap = URLMap.objects.filter(**filter_kwargs).cache(timeout=60 * 60 * 60).first()

        if not instance:
            raise Http404

        return instance

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        timeframe = request.query_params.get('timeframe', 1)
        user_specific = request.query_params.get('user_specific', 0)

        try:
            timeframe = int(timeframe)
            if timeframe not in [1, 7, 30]:
                timeframe = 1
        except ValueError:
            timeframe = 1

        try:
            user_specific = int(user_specific)
        except ValueError:
            user_specific = 0

        key = f'{user_specific}{timeframe}'

        if _is_cached(instance, timeframe, key):
            return Response(data=instance.cached_statistics[key])

        else:
            queryset = _query_builder(instance, _convert_time_frame_to_range(timeframe), user_specific)
            response = _build_response(queryset, user_specific, key=key)
            cache_statistics_in_disk.apply_async(kwargs={'instance': pickle.dumps(instance),
                                                         'response': response,
                                                         'field': _get_proper_field(timeframe)})
        return Response(data=response[key])


class CreatShortURLAPIView(CreateAPIView):
    queryset = URLMap.objects.all()
    serializer_class = CreateShortURLSerializer
    permission_classes = [IsAuthenticated]


class RedirectShortURLView(RetrieveAPIView):
    queryset = URLMap.objects.all()
    permission_classes = [AllowAny]
    lookup_field = 'short_url'

    def get_object(self):
        filter_kwargs = {self.lookup_field: self.kwargs[self.lookup_url_kwarg or self.lookup_field]}
        instance: URLMap = URLMap.objects.filter(**filter_kwargs).cache(timeout=60 * 60 * 60).first()

        if not instance:
            raise Http404

        return instance

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        save_history.apply_async(kwargs={'agent': pickle.dumps(request.user_agent),
                                         'user_id': request.user.pk,
                                         'browser': request.user_agent.browser.family,
                                         'url_id': instance.pk
                                         })

        return HttpResponseRedirect(redirect_to=instance.original_url)


redirect_view = RedirectShortURLView.as_view()
create_short_url = CreatShortURLAPIView.as_view()
statistics = URLStatisticsAPIView.as_view()

__all__ = [
    'create_short_url',
    'redirect_view',
    'statistics',
]
