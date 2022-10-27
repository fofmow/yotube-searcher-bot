from collections import deque
from typing import NamedTuple
from youtube_search import YoutubeSearch


class YouTubeVideo(NamedTuple):
    url: str
    title: str
    logo_url: str
    channel: str
    duration: str
    views: str
    publish_time: str


async def get_videos_by_query(query: str, max_results=3) -> deque[YouTubeVideo]:
    """ Сбор информации по найденным через запрос видео """

    dq = deque()

    videos = YoutubeSearch(query, max_results=max_results).to_dict()
    for v in videos:
        # duration, views и publish_time в случае трансляции имеют значения 0
        dq.append(YouTubeVideo(
            url=f"https://www.youtube.com/watch?v={v['id']}",
            title=v['title'],
            logo_url=v['thumbnails'][-1],
            channel=v['channel'],
            duration=v['duration'],
            views=v['views'] or "️Прямой Эфир",
            publish_time=v['publish_time'] or "Трансляция активна"
        ))

    return dq
