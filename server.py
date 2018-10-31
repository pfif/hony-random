import os
from random import randint
from typing import Dict, Optional

from flask import Flask, redirect
from mypy_extensions import TypedDict
from requests import Session

app = Flask(__name__)

Post = TypedDict(
    'Post', {"post_url": str, "caption": str, "timestamp": int, "slug": str})


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


def post_by_id(identifier: str) -> Optional[Post]:
    posts = query_posts({"id": identifier})
    if posts:
        raw_post = posts["response"]["posts"][0]
        post = parse_post(raw_post)
        app.logger.debug("Retrieved post by id : %s" % post["slug"])
        return post
    else:
        return None


def parse_post_number_in_series(post: Post) -> int:
    pass


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


def first_post(identifier: str) -> Optional[Post]:
    post = post_by_id(identifier)
    if post:
        position = parse_post_number_in_series(post)
        return nth_previous_posts(post, position - 1)
    else:
        return None


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


@app.route('/error/')
def random_exception():
    raise Exception()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port='80', debug=bool(os.getenv("DEV_MODE", "")))
