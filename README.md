One _Human of New York_ at random
=

Endpoints:
--

- `/` : Redirects to any story
- `/long/` : Redirects to a long story (over 500 char)

Run
--

- Production mode : `docker-compose up`
- Developement mode : `docker-compose -f docker-compose.yml -f docker-compose.up.yml up --build`
- Run tests : `docker-compose -f docker-compose.test.yml build && docker-compose -f docker-compose.test.yml run tests`

Todo (maybe, one day ...)
--

- Proper web server in production (currently, Flask's developement server is used)
- A homepage to introduce the different mode to the public
- Add static typing
