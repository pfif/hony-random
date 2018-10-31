from unittest.mock import patch

from requests_mock import Mocker

from server import (
    tumblr_session, posts_count, random_post, post_url, random_long_post,
    parse_post, post_by_id, nth_previous_posts, Post, query_posts)

TUMBLR_URL_POST = "https://api.tumblr.com/v2/blog/www.humansofnewyork.com/posts/photo/"
TUMBLR_URL_BLOG = "https://api.tumblr.com/v2/blog/www.humansofnewyork.com/info"

TUMBLR_RESPONSE_BLOG = """{
    "response": {
        "blog": {
            "total_posts": 7260
        }
    }
}"""


TUMBLR_RESPONSE_POST_TEXT = """{
    "response": {
        "posts": [
            {
                "slug": "a-slug",
                "post_url": "http://www.humansofnewyork.com/url",
                "caption": "<p>a_caption</p>",
                "timestamp": 1540424820
            }
        ]
    }
}"""


TUMBLR_RESPONSE_POST_JSON = {
    "response": {
        "posts": [
            {
                "slug": "a-slug",
                "post_url": "http://www.humansofnewyork.com/url",
                "caption": "<p>a_caption</p>",
                "timestamp": 1540424820
            }
        ]
    }
}


TUMBLR_POST = {
    "slug": "a-slug",
    "post_url": "http://www.humansofnewyork.com/url",
    "caption": "<p>a_caption</p>",
    "timestamp": 1540424820
}


TUMBLR_RESPONSE_THREE_POSTS = {
    "response": {
        "posts": [
            {
                "slug": "a-slug",
                "post_url": "http://www.humansofnewyork.com/url",
                "caption": "<p>a_caption</p>",
                "timestamp": 1540424820
            },
            {
                "slug": "a-slug",
                "post_url": "http://www.humansofnewyork.com/url",
                "caption": "<p>a_caption</p>",
                "timestamp": 1540424820
            },
            {
                "slug": "a-slug",
                "post_url": "http://www.humansofnewyork.com/url",
                "caption": "<p>a_caption_last</p>",
                "timestamp": 1540424820
            }
        ]
    }
}


TUMBLR_THREE_POSTS_LAST_POST = {
    "slug": "a-slug",
    "post_url": "http://www.humansofnewyork.com/url",
    "caption": "<p>a_caption_last</p>",
    "timestamp": 1540424820
}


def make_test_post(post_url: str = "http://www.humansofnewyork.com/url",
                   slug: str = "a-slug",
                   caption: str = "<p>a_caption</p>",
                   timestamp: int = 1540424820) -> Post:
    return {
        "post_url": post_url,
        "caption": caption,
        "timestamp": timestamp,
        "slug": slug
    }


def test_parse_post__parses_post_url():
    assert parse_post(TUMBLR_POST)["post_url"] == "http://www.humansofnewyork.com/url"  # noqa


def test_parse_post__parses_slug():
    assert parse_post(TUMBLR_POST)["slug"] == "a-slug"


def test_parse_post__parses_caption():
    assert parse_post(TUMBLR_POST)["caption"] == "<p>a_caption</p>"


def test_parse_post__parses_timestamp():
    assert parse_post(TUMBLR_POST)["timestamp"] == 1540424820


def test_tumblr_session_has_correct_key():
    with patch('server.os.environ', {"TUMBLR_API_KEY": "key"}):
        session = tumblr_session()

    assert session.params["api_key"] == "key"  # type: ignore


def test_query_posts__argument_passed():
    with Mocker() as m:
        m.get(TUMBLR_URL_POST, text=TUMBLR_RESPONSE_POST_TEXT)
        query_posts({"limit": "1", "offset": "10"})

    assert m.request_history[0].qs["limit"] == ['1']
    assert m.request_history[0].qs["offset"] == ['10']


def test_query_posts__filter_added():
    with Mocker() as m:
        m.get(TUMBLR_URL_POST, text=TUMBLR_RESPONSE_POST_TEXT)
        query_posts({"limit": "1", "offset": "10"})

    assert m.request_history[0].qs["filter"] == ['raw']


def test_query_posts__returns_json():
    with Mocker() as m:
        m.get(TUMBLR_URL_POST, text=TUMBLR_RESPONSE_POST_TEXT)
        response = query_posts({})

    assert response == TUMBLR_RESPONSE_POST_JSON


def test_query_posts__returns_none_if_does_not_exists():
    with Mocker() as m:
        m.get(TUMBLR_URL_POST, status_code=404)
        response = query_posts({})

    assert response is None


def test_post_count__returns_post():
    with Mocker() as m:
        m.get(TUMBLR_URL_BLOG, text=TUMBLR_RESPONSE_BLOG)
        count = posts_count()
    assert count == 7260


def test_random_post__passes_correct_post():
    parse_post_patch = patch("server.parse_post", side_effect=make_test_post)
    query_posts_patch = patch(
        "server.query_posts", side_effect=[TUMBLR_RESPONSE_POST_JSON])
    with parse_post_patch as parse_post_mock, query_posts_patch:
        random_post(1138)

    parse_post_mock.assert_called_with(TUMBLR_POST)


def test_random_post__selects_article():
    query_posts_patch = patch(
        "server.query_posts", side_effect=[TUMBLR_RESPONSE_POST_JSON])
    with query_posts_patch as query_posts_mock, patch("server.randint", side_effect=[10]):
        random_post(1138)

    query_posts_mock.assert_called_with(
        {"limit": 1, "offset": 10})


def test_post_url():
    assert post_url(make_test_post(post_url="url")) == "url"


def test_random_long_post__first_post_is_long_enough():
    post = make_test_post(caption="".join(["c" for i in range(501)]))

    with patch("server.random_post", side_effect=[post]):
        returned_post = random_long_post(1138)

    assert returned_post == post


def test_random_long_post__third_post_is_long_enough():
    posts = [
        make_test_post(caption="".join(["c" for i in range(300)])),
        make_test_post(caption="".join(["c" for i in range(100)])),
        make_test_post(caption="".join(["c" for i in range(501)]))
    ]

    with patch("server.random_post", side_effect=posts):
        returned_post = random_long_post(1138)

    assert returned_post == posts[2]


def test_post_by_id__passes_correct_post():
    parse_post_patch = patch("server.parse_post", side_effect=make_test_post)
    query_posts_patch = patch(
        "server.query_posts", side_effect=[TUMBLR_RESPONSE_POST_JSON])
    with query_posts_patch, parse_post_patch as parse_post_mock:
        post_by_id("4815162342")

    parse_post_mock.assert_called_with(TUMBLR_POST)


def test_post_by_id__return_none_if_do_not_exists():
    query_posts_patch = patch(
        "server.query_posts", side_effect=[None])
    with query_posts_patch:
        post = post_by_id("4815162342")

    assert post is None


def test_post_by_id__correct_argument_passed():
    query_posts_patch = patch(
        "server.query_posts", side_effect=[TUMBLR_RESPONSE_POST_JSON])
    with query_posts_patch as query_posts_mock:
        post_by_id("4815162342")

    query_posts_mock.assert_called_with({"id": "4815162342"})


def test_nth_previous_posts__correct_arguments_passed():
    query_posts_patch = patch(
        "server.query_posts", side_effect=[TUMBLR_RESPONSE_THREE_POSTS])
    with query_posts_patch as query_posts_mock:
        nth_previous_posts(make_test_post(timestamp=5555), 3)

    query_posts_mock.assert_called_with({
        "before": 5554,
        "limit": 3
    })


def test_nth_previous_posts__passes_correct_post():
    parse_post_patch = patch("server.parse_post", side_effect=make_test_post)
    query_posts_patch = patch(
        "server.query_posts", side_effect=[TUMBLR_RESPONSE_THREE_POSTS])
    with query_posts_patch, parse_post_patch as parse_post_mock:
        nth_previous_posts(make_test_post(timestamp=5555), 3)

    parse_post_mock.assert_called_with(TUMBLR_THREE_POSTS_LAST_POST)
