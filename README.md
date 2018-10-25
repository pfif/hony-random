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

Todo (maybe, one day ...)
--

- Write tests
- Proper web server in production (currently, Flask's developement server is used)
- A homepage to introduce the different mode to the public
- Maybe turn this into a Google App Engine app ?
