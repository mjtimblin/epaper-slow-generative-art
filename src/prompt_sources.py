import feedparser
import json
import random
import requests
from typing import Optional, Tuple

from prompt import Prompt

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
}

FALLBACK_PROMPT = Prompt(
    title='A cute kitten playing with a ball of yarn',
    prefix='',
    suffix='',
    url='https://cataas.com/cat/says/no%20valid%20article%20found',
)


def __get_random_prefix_and_suffix() -> Tuple[str, str]:
    prefix = random.choice([
        'Baroque-style scene with (',
        'Anime scene with (',
        'Gothic painting of (',
        'Documentary-style photography of (',
        'Selfie with (',
        'Futuristic style photo of (',
    ])
    suffix = random.choice([
        ')',
        '). Concept art, detail, sharp focus',
        '). Calm, realistic, Volumetric Lighting',
        '). Clear definition, unique and one-of-a-kind piece.',
        '). Gloomy, dramatic, stunning, dreamy',
        '). Anime, cartoon',
    ])
    return prefix, suffix


def __get_web_content(url: str) -> Optional[str]:
    try:
        return requests.get(url, headers=HEADERS).text
    except Exception as e:
        print(e)
        return None


def __get_title_and_url_from_rss_feed(rss_url: str) -> Tuple[Optional[str], Optional[str]]:
    feed = feedparser.parse(rss_url, agent=HEADERS['User-Agent'])

    if not feed or not feed.entries or len(feed.entries) == 0:
        return None, None

    title = feed.entries[0].title
    url = feed.entries[0].link

    return title, url


# -----------------------------------------------------------------------------
# To add a new source, create a function that returns a Prompt object.
# The prefix and suffix attributes can be empty strings since they will be
# overwritten. The function should return None if it fails to get a prompt.
# Then add the function to the sources list in get_random_prompt().
# -----------------------------------------------------------------------------

def __bbc() -> Optional[Prompt]:
    title, url = __get_title_and_url_from_rss_feed('https://feeds.bbci.co.uk/news/world/rss.xml')

    if not title or not url:
        return None

    return Prompt(
        title=title,
        prefix='',
        suffix='',
        url=url,
    )


def __cnn() -> Optional[Prompt]:
    title, url = __get_title_and_url_from_rss_feed('http://rss.cnn.com/rss/cnn_latest.rss')

    if not title or not url:
        return None

    return Prompt(
        title=title,
        prefix='',
        suffix='',
        url=url,
    )


def __onion() -> Optional[Prompt]:
    title, url = __get_title_and_url_from_rss_feed('https://www.theonion.com/rss')

    if not title or not url:
        return None

    return Prompt(
        title=title,
        prefix='',
        suffix='',
        url=url,
    )


def __reddit_not_the_onion() -> Optional[Prompt]:
    response = __get_web_content("https://www.reddit.com/r/nottheonion/new/.json?limit=10")

    if not response:
        return None

    data = json.loads(response)

    posts = []
    if data and 'data' in data and 'children' in data['data']:
        for post in data['data']['children']:
            if post['kind'] == 't3':
                posts.append(post['data'])

    if len(posts) == 0:
        return None

    return Prompt(
        title=posts[0]['title'],
        prefix='',
        suffix='',
        url="https://www.reddit.com" + posts[0]['permalink'],
    )


def get_random_prompt(blacklisted_titles=None) -> Prompt:
    if blacklisted_titles is None:
        blacklisted_titles = []

    prompt = None

    sources = [
        __bbc,
        __cnn,
        __onion,
        __reddit_not_the_onion,
    ]
    sources_without_response = []

    while not prompt and len(sources) > 0:
        source = random.choice(sources)

        if source in sources_without_response:
            continue

        prompt = source()

        if not prompt or prompt.title in blacklisted_titles:
            prompt = None
            sources_without_response.append(source)
            sources.remove(source)

    if not prompt:
        prompt = FALLBACK_PROMPT

    prefix, suffix = __get_random_prefix_and_suffix()
    prompt.prefix = prefix
    prompt.suffix = suffix

    return prompt
