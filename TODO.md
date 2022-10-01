# GareFixer

Movie library metadata fixer

## TODO items

- [x] quick fix to match if there is an exact match in search and no duplicate exact matches
- [ ] create a worker pool to db group stuff in parallel (need new version of Alchemy)
- [ ] convert to alchemy, to utilize asyncio
- [ ] convert to posgre
- [-] remove concept of bad imdb, just dont attach any og query
- [x] set up launch file for browser debugger integration
- [x] update confident  match funtion to use tmdb and imdb
- [x] make confident match function case insensitive
- [x] make a singular button on review page to remove imdb search
- [x] make a way to backup database and restore it
- [ ] refactor data modifiers to be more generic, like the query modifiers
- [ ] implement thread pool/asyncio for tmdb searches!
