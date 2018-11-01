import re
import os
from random import randint
from typing import Dict, List, Optional, NewType

from flask import Flask, redirect
from mypy_extensions import TypedDict
from requests import Session

app = Flask(__name__)

Post = TypedDict(
    'Post', {"post_url": str, "caption": str, "timestamp": int, "slug": str})

PostIdentifier = NewType('PostIdentifier', int)


def parse_post(raw_post: Dict) -> Post:
    return {
        "post_url": raw_post["post_url"],
        "caption": raw_post["caption"],
        "timestamp": raw_post["timestamp"],
        "slug": raw_post["slug"]
    }


def tumblr_session() -> Session:
    s = Session()
    s.params = {
        "api_key": os.getenv('TUMBLR_API_KEY', '')
    }
    return s


def posts_count() -> int:
    blog = tumblr_session().get(
        "https://api.tumblr.com/v2/blog/www.humansofnewyork.com/info")
    blog.raise_for_status()

    result = blog.json()["response"]["blog"]["total_posts"]
    app.logger.debug("Retrieved post count: %s" % result)
    return result


def query_posts(params: Dict) -> Optional[dict]:
    params["filter"] = "raw"

    post_query = tumblr_session().get(
        "https://api.tumblr.com/v2/blog/www.humansofnewyork.com/posts/photo/",
        params=params)
    if post_query.status_code == 200:
        return post_query.json()
    elif post_query.status_code == 404:
        return None
    else:
        post_query.raise_for_status()

    return post_query.json()


def random_post(posts_count: int) -> Optional[Post]:
    post_nb = randint(0, posts_count)

    posts = query_posts({
        "limit": 1,
        "offset": post_nb
    })

    if posts is not None:
        raw_post = posts["response"]["posts"][0]
        post = parse_post(raw_post)
        app.logger.debug("Retrieved post randomly : %s" % post["slug"])
        return post
    else:
        return None


def post_by_id(identifier: PostIdentifier) -> Optional[Post]:
    posts = query_posts({"id": identifier})
    if posts:
        raw_post = posts["response"]["posts"][0]
        post = parse_post(raw_post)
        app.logger.debug("Retrieved post by id : %s" % post["slug"])
        return post
    else:
        return None


def parse_post_number_in_series(post: Post) -> Optional[int]:
    match = re.search(r"\((\d{1,2})/\d{1,2}\)", post["caption"])
    if match:
        return int(match.group(1))
    else:
        return None


def nth_previous_posts(post: Post, n: int) -> Optional[Post]:
    posts = query_posts({
        "before": (post["timestamp"] - 1),
        "limit": n
    })

    if posts is not None:
        raw_post = posts["response"]["posts"][-1]
        post = parse_post(raw_post)
        app.logger.debug("Retrieved %s previous post : %s" % (n, post["slug"]))
        return post
    else:
        return None


def first_post(identifier: PostIdentifier) -> Optional[Post]:
    post = post_by_id(identifier)
    position = parse_post_number_in_series(post) if post else None
    return nth_previous_posts(post, position - 1) if post and position else None


def post_url(post: Post) -> str:
    return post["post_url"]


def random_long_post(posts_count: int) -> Optional[Post]:
    post = random_post(posts_count)
    if post:
        post_length = len(post["caption"])
        app.logger.debug("Counted length for post : %s" % post_length)

        if post_length > 500:
            return post
        else:
            return random_long_post(posts_count)
    else:
        return None


def next_post(identifier: PostIdentifier) -> Optional[Post]:
    current_post = post_by_id(identifier)

    if current_post:
        timestamp_next_day = current_post["timestamp"] + (60 * 60 * 24)
        posts = posts_before(timestamp_next_day)

        return find_following_post(posts, current_post)
    return None


def posts_before(timestamp: int) -> List[Post]:
    raw_posts = query_posts({"before": timestamp})
    if raw_posts:
        return [
            parse_post(raw_post)
            for raw_post in raw_posts["response"]["posts"]]
    return []


def find_following_post(posts: List[Post], current_post: Post) -> Optional[Post]:
    for i, post in enumerate(posts):
        if post == current_post and (i - 1) > 0:
            return posts[i - 1]
    return None


@app.route('/')
def redirect_to_random_post():
    post = random_post(posts_count())
    if post:
        return redirect(post_url(post), code=303)


@app.route('/long/')
def redirect_to_random_long_post():
    post = random_long_post(posts_count())
    if post:
        return redirect(post_url(post), code=303)


@app.route('/first/post/<int:post_id>/<path:after>/')
def redirect_to_first_post(post_id, after):
    post = first_post(post_id)
    if post:
        return redirect(post_url(post), code=303)
    else:
        return "Something went wrong. Does your article exists?"


@app.route('/next/post/<int:post_id>/<path:after>/')
def redirect_to_next_post(post_id, after):
    post = next_post(post_id)
    if post:
        return redirect(post_url(post), code=303)
    else:
        return "Something went wrong. Does your article exists?"


@app.route('/error/')
def random_exception():
    raise Exception()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port='80', debug=bool(os.getenv("DEV_MODE", "")))
