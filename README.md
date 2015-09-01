elasticsearch-collectd-plugin
=====================

An [ElasticSearch](http://elasticsearch.org) plugin for [collectd](http://collectd.org) using collectd's [Python plugin](http://collectd.org/documentation/manpages/collectd-python.5.shtml).

Node stats :
 * Docs (total docs & deleted docs)
 * Store size
 * Indexing (total, time, total delete, delete time)
 * Get (total, time, exists total, exists time, missing total, missing time)
 * Search (total query, total time, total fetch, total fetch time)
 * JVM memory (heap commited, heap Used, non heap commited, non heap used)
 * JVM threads (count & peak)
 * JVM GC (time & count)
 * Transport stats (server open, RX count, RX size, TX count, TX size)
 * HTTP stats (current open & total open)
 * OS stats (CPU percent, file descriptors)
 * Thread pool stats (generic, index, get, snapshot, merge, optimize, bulk, warmer, flush, search, refresh)
 * Cache (field eviction, field size, filter evictions, filter size)
 * JVM collectors
 * FLush (total count, total time)
 * Merges (current count, current docs, current size, merge total size, docs a time)
 * Refresh (Total & Time)

Index stats:
 * Transaction log (size, number of operations)
 * Most of the common stats per index and per primary vs. total.

Cluster stats:
 * Shard stats (active, initializing, relocating, unassigned, primaries)
 * Nodes (total, data nodes)


Install
-------
 1. Place elasticsearch_collectd.py in /opt/collectd/lib/collectd/plugins/python (assuming you have collectd installed to /opt/collectd).
 2. Configure the plugin (see below).
 3. Restart collectd.

Configuration
-------------
 * See elasticsearch.conf
 * The plugin will automatically determine the version of elasticsearch.
 * Per index and cluster stats can be disabled if needed. They are enabled by default.

Requirements
------------
 * collectd 4.9+
 * Elasticsearch 1.x or later.
