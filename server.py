import os
from random import randint

from flask import Flask, redirect
from requests import Session

app = Flask(__name__)


class Post(object):
    def __init__(self, post_url, caption, timestamp):
        self.post_url = post_url
        self.caption = caption
        self.timestamp = timestamp


def tumblr_session():
    s = Session()
    s.params = {
        "api_key": os.getenv('TUMBLR_API_KEY', '')
    }
    return s


def posts_count():
    blog = tumblr_session().get(
        "https://api.tumblr.com/v2/blog/www.humansofnewyork.com/info")
    blog.raise_for_status()

    result = blog.json()["response"]["blog"]["total_posts"]
    app.logger.debug("Retrieved post count: %s" % result)
    return result


def random_post(posts_count):
    post_nb = randint(0, posts_count)

    post = tumblr_session().get(
        "https://api.tumblr.com/v2/blog/www.humansofnewyork.com/posts/photo/",
        params={
            "limit": 1,
            "offset": post_nb
        })
    post.raise_for_status()

    result = post.json()["response"]["posts"][0]
    app.logger.debug("Retrieved post randomly : %s" % result["slug"])
    return Post(result["post_url"], result["caption"], result["timestamp"])


def post_by_id(identifier):
    post = tumblr_session().get(
        "https://api.tumblr.com/v2/blog/www.humansofnewyork.com/posts/photo/",
        params={
            "id": identifier
        }
    )

    if post.status_code == 200:
        result = post.json()["response"]["posts"][0]
        app.logger.debug("Retrieved post by id : %s" % result["slug"])
        return Post(result["post_url"], result["caption"], result["timestamp"])
    elif post.status_code == 404:
        return None
    else:
        post.raise_for_status()


def parse_post_number_in_series(post):
    pass


def nth_previous_posts(post, n):
    posts = tumblr_session().get(
        "https://api.tumblr.com/v2/blog/www.humansofnewyork.com/posts/photo/",
        params={
            "before": (post.timestamp - 1),
            "limit": n
        }
    )

    result = posts.json()["response"]["posts"][-1]
    app.logger.debug("Retrieved %s previous post : %s" % (n, result["slug"]))
    return Post(result["post_url"], result["caption"], result["timestamp"])


def first_post(identifier):
    post = post_by_id(identifier)
    if post:
        position = parse_post_number_in_series(post)
        return nth_previous_posts(post, position - 1)
    else:
        return None


def post_url(post):
    return post.post_url


def random_long_post(posts_count):
    post = random_post(posts_count)
    post_length = len(post.caption)
    app.logger.debug("Counted length for post : %s" % post_length)

    if post_length > 500:
        return post
    else:
        return random_long_post(posts_count)


@app.route('/')
def redirect_to_random_post():
    return redirect(post_url(random_post(posts_count())), code=303)


@app.route('/long/')
def redirect_to_random_long_post():
    return redirect(post_url(random_long_post(posts_count())), code=303)


@app.route('/error/')
def random_exception():
    raise Exception()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port='80', debug=bool(os.getenv("DEV_MODE", "")))
