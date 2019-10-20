# strava-cli

Command line interface for [Strava](http://www.strava.com). It allows to:

* Retrieve infomations and stats about your activities matching certain criteria
* Bulk update activities

## Using strava-cli

```
$ ./strava-cli.py -h
usage: strava-cli.py [-h]
                     {activities,details,update,bikes,clear-cache,authenticate,store-token}
                     ...

Strava Command Line Interface

positional arguments:
  {activities,details,update,bikes,clear-cache,authenticate,store-token}
    activities          List activities according to specified filters
    details             Retrieves the details of one or more activities
    update              Update one or more activities
    bikes               Retrieve bikes
    clear-cache         Clear the cache
    authenticate        Authenticate using a client secret and client id

optional arguments:
  -h, --help            show this help message and exit
```

## Obtaining a token

Strava uses a 3-legged OAuth flow in order to allow the application to access user data. In the *Settings* page, *My API Application* section, you can find an authorization token... which actually doesn't work: some API calls (retrieving activites, for instance), return an empty result.

To obtain an access token:

* Obtain a client id and a client secret from Strava
* Execute

  ```
  $ ./strava-cli.py authenticate -i <client-id> -s <client-secret>
  ```
  Then navigate to `http://localhost:8080` (unless you've specified a different port with `--port`) using a web browser. You should be redirected to a page where Strava asks you to authorize the application. Once you've granted access to the application, Strava should send you back to local web server where a page should show a confirm that token has been stored.
  Please notice that **client id, client secret, access token and refresh token will be saved in your home directory in plain text**. This is necessary to refresh the access token automatically without having to re-login every time the access token expires.


### Retrieving activities

You can retrieve your activities using the `activities` subcommand. Activities are downloaded and cached locally; every time the command is run the application checks if new activities have been uploaded. To clear the cache you can use the Command

```
$ ./strava-cli.py clear-cache
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
* `elevation=[MIN]-[MAX]`
* `distance=[MIN]-[MAX]`

Some examples:

* Retrieve all your activities:

```
$ ./strava-cli activities
```

* Retrieve only private sessions:

```
$ ./strava-cli activities -f private=1
```

* Retrieve private sessions in january 2017:

```
$ ./strava-cli activities -f private=1 -f after=201701 -f before=201702
```

* Retrieve rides of 2016 with at least 1200m of elevation gain:

```
$ ./strava-cli.py activities -f before=20161231 -f after=20160101 -f  elevation=1200-

```


### Retrieving activity details

TODO

### Updating activities

You can update one ore more activities using the `update` command. The syntax is:

```
$ ./strava-cli.py update -h
usage: strava-cli.py update [-h] --set SET id [id ...]

positional arguments:
  id                 Activity id(s)

optional arguments:
  -h, --help         show this help message and exit
  --set SET, -s SET  Sets a property
```

Supported properties are described in the [Strava API v3 specification](https://strava.github.io/api/v3/activities/#put-updates).

When an update operation is performed the cache is updated accordingly; on the other hand updating an activity using another requires to clear the `strava-cli` cache in order to see the updated values.

* Change name and description of an activity:

```
$ ./strava-cli.py update -s "name=New activity name" -s "description=New activity description" <activity-id>
```

* Make all your indoor activities private:

```
$ ./strava-cli.py update -s private=true $(./strava-cli.py -t <token> activities -q -f trainer=true)
```

### Listing gear

```
$ ./strava-cli.py bikes
```

## TODO

* Support `--format` option to format output
* Implement activity detail
* Implement filter for activity title
* Implement command for total distance and climb
* Performance: flush the cache just once
