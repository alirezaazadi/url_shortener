import pickle

from app_shortener.models import *
from django.utils.timezone import now
from url_shortener.celery import celery_app


@celery_app.task(name='app_shortener.tasks.save_history')
def save_history(agent, **kwargs):
    agent = pickle.loads(agent)
    platform = History.Platform.OTHER

    if agent.is_mobile:
        platform = History.Platform.MOBILE
    elif agent.is_pc:
        platform = History.Platform.PC

    History.objects.create(platform=platform, **kwargs)
    # cache.incr(key=kwargs['url_id'], ignore_key_check=True)


@celery_app.task(name='app_shortener.tasks.cache_statistics_in_disk')
def cache_statistics_in_disk(instance, field, response):
    instance = pickle.loads(instance)

    cached_statistics: dict = instance.cached_statistics
    cached_statistics.update(response)
    instance.cached_statistics = cached_statistics
    fields = ['cached_statistics']
    if field:
        setattr(instance, field, now())
        fields.append(field)

    instance.save(update_fields=fields)


@celery_app.task
def daily_building_reports():
    from app_shortener.views import _query_builder, _build_response
    from app_shortener.views import _convert_time_frame_to_range
    from app_shortener.views import _get_proper_field

    for url in URLMap.objects.all().iterator():
        for timeframe in [7, 30]:
            for user_specific in [0, 1]:
                key = f'{user_specific}{timeframe}'
                queryset = _query_builder(url, _convert_time_frame_to_range(timeframe), user_specific)
                response = _build_response(queryset, user_specific, key=key)
                cache_statistics_in_disk.apply_async(kwargs={'instance': pickle.dumps(url),
                                                             'response': response,
                                                             'field': _get_proper_field(timeframe)})


@celery_app.task
def continuous_building_reports():
    from app_shortener.views import _query_builder, _build_response
    from app_shortener.views import _convert_time_frame_to_range
    from app_shortener.views import _get_proper_field

    for url in URLMap.objects.all().iterator():
        for user_specific in [0, 1]:
            key = f'{user_specific}{1}'
            queryset = _query_builder(url, _convert_time_frame_to_range(1), user_specific)
            response = _build_response(queryset, user_specific, key=key)
            cache_statistics_in_disk.apply_async(kwargs={'instance': pickle.dumps(url),
                                                         'response': response,
                                                         'field': _get_proper_field(1)})
