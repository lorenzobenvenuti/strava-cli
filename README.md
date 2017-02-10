# strava-cli

Command line interface for [Strava](http://www.strava.com).

## Obtaining a token

Strava uses a 3-legged OAuth flow in order to allow the application to access user data.
To obtain an access token:

* Obtain a client id and a client secret from Strava
* Execute `strava-get-token.py` passing the client id and client secret. Point a web browser to `http://localhost:8080` (unless you've specified a different port with `--port`); it should be redirected to a page where Strava asks you to authorize the application. Once you've granted access to the application, Strava should send you back to local web server where a page will show the authentication token.

## Using strava-cli

```
$ ./strava-cli.py -h
usage: strava-cli.py [-h] --token TOKEN
                     {activities,update,details,bikes,clear-cache} ...

Strava Command Line Interface

positional arguments:
  {activities,update,details,bikes,clear-cache}
    activities          List activities according to specified filters
    update              Update one or more activities
    details             Retrieves the details of one or more activities
    bikes               Retrieve bikes
    clear-cache         Clear the cache

optional arguments:
  -h, --help            show this help message and exit
  --token TOKEN, -t TOKEN
                        Strava API access token
```

### Retrieving activities

You can retrieve your activities using the `activities` subcommand. Activities are downloaded and cached locally; every time the command is run the application checks if new activities have been uploaded. To clear the cache you can use the Command

```
$ ./strava-cli.py -t <token> clear-cache
```

The `activities` command accepts some arguments:

```
$ ./strava-cli.py activities -h
usage: strava-cli.py activities [-h] [--filter FILTER] [--quiet]

optional arguments:
  -h, --help            show this help message and exit
  --filter FILTER, -f FILTER
                        Adds a filter to the query
  --quiet, -q           Prints only activity identifiers
```

The `--filter` (or `-f`) option allows you to filter activities. Supported filters are:

* `after=YYYY[MM[DD]]`
* `before=YYYY[MM[DD]]`
* `trainer=0|1|true|false`
* `private=0|1|true|false`

Some examples:

* Retrieve all your activities:

```
$ ./strava-cli -t <token> activities
```

* Retrieve only private sessions:

```
$ ./strava-cli -t <token> activities -f private=1
```

* Retrieve private sessions in january 2017:

```
$ ./strava-cli -t <token> activities -f private=1 -f after=201701 -f before=201702
```

### Retrieving activity details

TODO

### Updating activities

TODO

### Listing gear

```
$ ./strava-cli.py -t <token> bikes
```
