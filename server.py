import os
from random import randint

from flask import Flask, redirect
from requests import Session


app = Flask(__name__)


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
    app.logger.debug("Retrieved post : %s" % result["slug"])
    return result


def post_url(post):
    return post["post_url"]


def random_long_post(posts_count):
    post = random_post(posts_count)
    post_length = len(post["caption"])
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
