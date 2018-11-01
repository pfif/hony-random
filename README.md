One _Human of New York_ at random
=

Endpoints:
--

- `/` : Redirects to any story
- `/long/` : Redirects to a long story (over 500 char)
- `/first/post/{post_id}/any/path` : Redirect to the first post in a series
- `/next/post/{post_id}/any/path` : Redirect to the next post in a series

Run
--

- Production mode : `docker-compose up`
- Developement mode : `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build`
- Run tests : `mypy --ignore-missing-imports --check-untyped-defs tests.py server.py && pytest tests.py`

Todo (maybe, one day ...)
--

- Proper web server in production (currently, Flask's developement server is used)
- A homepage to introduce the different mode to the public
- Monad style error handling

Tech debt (maybe, one day ...)
--

- Break files up and make properties-based tests
- Proper logging on production
- Dependency security fix
- Make `nth_previous_posts` use `posts_before`
- Use `ContextManager`s in tests
