# Login

Lives at `login.datasektionen.se`. Uses [CAS](https://en.wikipedia.org/wiki/Central_Authentication_Service) to talk with https://login.kth.se. Fetches user info from KTH ldap at ldap.kth.se:389.

## Local setup for development of other services
The easiest way to get login running locally for development on another system
is to not use login but instead,
[nyckeln-under-dörrmattan](https://github.com/datasektionen/nyckeln-under-dorrmattan).

## Environment variables:

All defaults are sane for production. The only thing that needs to be set in production is `DATABASE_URL`.

| Variable               | Description                                                            | Example                               | Default                                           |
|------------------------|------------------------------------------------------------------------|---------------------------------------|---------------------------------------------------|
| SECRET_KEY             | Used for flasks sessions. Should be securely random and very secret.   | --                                    | (If none is supplied a secure value is generated.) |
| DATABASE_URL           | A postgresql database url.                                             | postgres://postgres:password@db:5432/ | --                                                |
| CAS_SERVER             | URL to authetication server.                                           | --                                    | https://login.kth.se                              |
| CAS_LOGIN_ROUTE        | --                                                                     | --                                    | /p3/login                                         |
| CAS_LOGOUT_ROUTE       | --                                                                     | --                                    | /p3/logout                                        |
| CAS_VALIDATE_ROUTE     | --                                                                     | --                                    | /p3/serviceValidate                               |
| MOCK_LDAP              | 1 if LDAP connection should be mocked, 0 if KTH's LDAP should be used. | 1 or 0                                | 0                                                 |
| DONT_VALIDATE_CALLBACK | Tells Login to not validate the callback provided to /login.           | 1 or 0                                | 0                                                 |

## Endpoints

### /hello

Returns `"Hello Login!"`. This endpoint is used for health-checks (a monitoring service checks that this endpoint returns a 200 status code).

### /login?callback=...

Must be called with parameter `callback` set to a url.

After the user has authenticated, the server will redirect to `callback` with the user's token appended at the end.

### /logout

Logs a user out.

### /verify/\<token\>?api_key=...

This is used to validate a user's token. Supply the token generated by `/login` in the path and a valid `api_key` and the server will answer with who the token belongs to. The response will be in JSON with the following format:

```json
{
    "first_name": "...",
    "last_name": "...",
    "user": "...",
    "emails": "...",
    "ugkthid": "..."
}
```

Note that `ugkthid` is on the form `u1xxxxx` and that `user` is the "normal" kthid that is part of a users' KTH email address. The API key should be generated from [pls](https://github.com/datasektionen/pls).

## Development setup

First install [docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/). Then run:

```sh
[sudo] docker-compose up --build
```

`Ctrl+C` can be used to stop the server. The site will be available at [http://localhost:8000](http://localhost:8000).

To access the db directly run:

```sh
[sudo] docker-compose exec db psql --username=postgres
```

To generate an `api_key` using `genkey.py` run:

```sh
[sudo] docker-compose exec web pipenv run python genkey.py <keyname>
```

These test users exist:

- juland
- tanlar
- gopgus

They all have the password: `rudolf`.

## Production setup

Build the Dockerfile, run the container. The environment variable `DATABASE_URL` needs to be set to a postgresql database url.

## Dependency on other systems at Datasektionen

Login uses [Pls](https://pls.datasektionen.se) to validate API keys. The API keys must have the "login" permission in the "login" system.
