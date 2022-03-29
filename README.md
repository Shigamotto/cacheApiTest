# Cache Api Project

This project created for a Interview Test Task.

###Following features have to be implemented for the cache:

- Add an endpoint that returns the cached data for a given key.
    - If the key is not found in the cache:
    - Log an output “Cache Miss”.
    - Create a random string.
    - Update the cache with this random string.
    - Return the random string.
- If the key is found in the cache:
  - Log an output “Cache Hit”.
  - Get the data for this key.
  - Return the data.
- Add an endpoint that returns all stored keys in the cache.
- Add an endpoint that creates/updates the data for a given key.
- Add an endpoint that removes a given key from the cache.
- Add an endpoint that removes all keys from the cache.

### Following additional features have to be also included:

- The number of entries allowed in the cache is limited. If the maximum amount of
cached items is reached, some old entry needs to be overwritten (Please explain the
approach of what is overwritten in the comments of the source code).
- Every cached item has a Time To Live (TTL). If the TTL is exceeded, the cached data will
not be used. A new random value will then be generated (just like cache miss). The TTL
will be reset on every read/cache hit.

## Start the project

To start project clone repo, and run `docker-compose up -d --build`.
After that go to `http://127.0.0.1:8080/swagger/` and start using `http://127.0.0.1:8080/<cache_path_from_swagger>/`.

For testing you can use django_rest_framework interface like `http://127.0.0.1:8080/cache/list/`.

Also you can check [tests](./app/cache/test.py), to understand how it works.