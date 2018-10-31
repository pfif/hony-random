One _Human of New York_ at random
=

Endpoints:
--

- `/` : Redirects to any story
- `/long/` : Redirects to a long story (over 500 char)

Run
--

- Production mode : `docker-compose up`
- Developement mode : `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build`
- Run tests : `mypy --ignore-missing-imports --check-untyped-defs tests.py server.py && pytest tests.py`

Todo (maybe, one day ...)
--

- Proper web server in production (currently, Flask's developement server is used)
- A homepage to introduce the different mode to the public


Tech debt (maybe, one day ...)
--

- Break files up
- Proper logging on production
- Dependency security fix
