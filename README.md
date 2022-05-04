### TiSrv

TiSrv is a tile server that try to implement  [OGC API – Tiles](https://ogcapi.ogc.org/tiles/), currently only vector tile is supported. 

The following [OGC API – Tiles](https://ogcapi.ogc.org/tiles/) comformance classes are implemented: Core, TileSet, TileSets List, Geo Data Resource Tilesets. 

TiSrv is built on top of these software: [FastAPI](https://github.com/tiangolo/fastapi), [morecantile](https://github.com/developmentseed/morecantile), [asyncpg](https://github.com/MagicStack/asyncpg). And special thanks to  **[pg_tileserv](https://github.com/CrunchyData/pg_tileserv)** for its excellent SQL template.

### How to run

Unix like environment:

```bash
git clone https://github.com/kikitte/tisrv.git tisrv

# change working directory
cd tisrv

# preparing virtual env
python -m venv venv
source venv/bin/activate

# install dependencies
pip install -r requirements.txt

# start server, Note: before you starting the server, the configuration file may be edited.
uvicorn tisrv.main:app
```

The configuration file is `tisrv.conf`, and it should be placed in the root of working directory. Please check `tisrv.conf` for more detail about configuration.

### Consume the service

Clients that flows the [OGC API – Tiles](https://ogcapi.ogc.org/tiles/) should play well with this service, for example tileset endpoint can be used by openlayers, see [OpenLayers - OGC Vector Tiles](https://openlayers.org/en/latest/examples/ogc-vector-tiles.html).

### Implementation Details

Vector Tile:

- A **geospatial data resource** represents a spatial table in database.
- A **dataset** represents a scheme in database.

### Benchmark/Comparing

fetch 64848 vector tile from pg_tileserv and tisrv: 

```bash
siege --reps=once --no-parser -b -f tiles-l15.txt 

# pg_tileserv with gzip disabled (the default)
Transactions:                  64848 hits
Availability:                 100.00 %
Elapsed time:                  41.68 secs
Data transferred:             557.59 MB
Response time:                  0.02 secs
Transaction rate:            1555.85 trans/sec
Throughput:                    13.38 MB/sec
Concurrency:                   24.47
Successful transactions:       64848
Failed transactions:               0
Longest transaction:            0.08
Shortest transaction:           0.00
Shortest transaction:           0.00

# pg_tileserv with gzip disabled (self compiled to disable gzip)
Transactions:                  64848 hits
Availability:                 100.00 %
Elapsed time:                  36.50 secs
Data transferred:            1085.54 MB
Response time:                  0.01 secs
Transaction rate:            1776.66 trans/sec
Throughput:                    29.74 MB/sec
Concurrency:                   24.58
Successful transactions:       64848
Failed transactions:               0
Longest transaction:            0.06
Shortest transaction:           0.00

# tisrv with gzip disabled
Transactions:                  64848 hits
Availability:                 100.00 %
Elapsed time:                  70.53 secs
Data transferred:            1085.51 MB
Response time:                  0.03 secs
Transaction rate:             919.44 trans/sec
Throughput:                    15.39 MB/sec
Concurrency:                   24.77
Successful transactions:       64848
Failed transactions:               0
Longest transaction:            0.15
Shortest transaction:           0.00

# tisrv with gzip enabled
Transactions:                  64848 hits
Availability:                 100.00 %
Elapsed time:                 125.34 secs
Data transferred:             556.87 MB
Response time:                  0.05 secs
Transaction rate:             517.38 trans/sec
Throughput:                     4.44 MB/sec
Concurrency:                   24.77
Successful transactions:       64848
Failed transactions:               0
Longest transaction:            0.18
Shortest transaction:           0.00
```

