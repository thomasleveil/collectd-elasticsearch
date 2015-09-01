#! /usr/bin/python
# Copyright 2014 Jeremy Carroll
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import json
import urllib2
import collections

PREFIX = "elasticsearch"
ES_CLUSTER = "elasticsearch"
ES_HOST = "localhost"
ES_PORT = 9200
ES_VERSION = "1.0"

ENABLE_INDEX_STATS = True
ENABLE_CLUSTER_STATS = True

ES_NODE_URL = ""
ES_CLUSTER_URL = ""
ES_INDEX_URL = ""
ES_INDEX = []

VERBOSE_LOGGING = False

Stat = collections.namedtuple('Stat', ('type', 'path'))

NODE_STATS_CUR = {}
INDEX_STATS_CUR = {}
CLUSTER_STATS_CUR = {}

# DICT: ElasticSearch 1.0.0
NODE_STATS_ES1 = {
    # STORE
    'indices.store.throttle-time': Stat("counter", "nodes.%s.indices.store.throttle_time_in_millis"),

    # SEARCH
    'indices.search.open-contexts': Stat("gauge", "nodes.%s.indices.search.open_contexts"),

    # CACHE
    'indices.cache.field.eviction': Stat("counter", "nodes.%s.indices.fielddata.evictions"),
    'indices.cache.field.size': Stat("bytes", "nodes.%s.indices.fielddata.memory_size_in_bytes"),
    'indices.cache.filter.evictions': Stat("counter", "nodes.%s.indices.filter_cache.evictions"),
    'indices.cache.filter.size': Stat("bytes", "nodes.%s.indices.filter_cache.memory_size_in_bytes"),

    # GC
    'jvm.gc.time': Stat("counter", "nodes.%s.jvm.gc.collectors.young.collection_time_in_millis"),
    'jvm.gc.count': Stat("counter", "nodes.%s.jvm.gc.collectors.young.collection_count"),
    'jvm.gc.old-time': Stat("counter", "nodes.%s.jvm.gc.collectors.old.collection_time_in_millis"),
    'jvm.gc.old-count': Stat("counter", "nodes.%s.jvm.gc.collectors.old.collection_count"),

    # FLUSH
    'indices.flush.total': Stat("counter", "nodes.%s.indices.flush.total"),
    'indices.flush.time': Stat("counter", "nodes.%s.indices.flush.total_time_in_millis"),

    # MERGES
    'indices.merges.current': Stat("gauge", "nodes.%s.indices.merges.current"),
    'indices.merges.current-docs': Stat("gauge", "nodes.%s.indices.merges.current_docs"),
    'indices.merges.current-size': Stat("bytes", "nodes.%s.indices.merges.current_size_in_bytes"),
    'indices.merges.total': Stat("counter", "nodes.%s.indices.merges.total"),
    'indices.merges.total-docs': Stat("gauge", "nodes.%s.indices.merges.total_docs"),
    'indices.merges.total-size': Stat("counter", "nodes.%s.indices.merges.total_size_in_bytes"),
    'indices.merges.time': Stat("counter", "nodes.%s.indices.merges.total_time_in_millis"),

    # REFRESH
    'indices.refresh.total': Stat("counter", "nodes.%s.indices.refresh.total"),
    'indices.refresh.time': Stat("counter", "nodes.%s.indices.refresh.total_time_in_millis"),

    # SEGMENTS
    'indices.segments.count': Stat("gauge", "nodes.%s.indices.segments.count"),
    'indices.segments.size': Stat("bytes", "nodes.%s.indices.segments.memory_in_bytes"),
}

# DICT: ElasticSearch 0.9.x
NODE_STATS_ES09 = {

    # GC
    'jvm.gc.time': Stat("counter", "nodes.%s.jvm.gc.collection_time_in_millis"),
    'jvm.gc.count': Stat("counter", "nodes.%s.jvm.gc.collection_count"),

    # CPU
    'process.cpu.percent': Stat("gauge", "nodes.%s.process.cpu.percent"),
}

# DICT: Common stuff
NODE_STATS = {

    # DOCS
    'indices.docs.count': Stat("gauge", "nodes.%s.indices.docs.count"),
    'indices.docs.deleted': Stat("gauge", "nodes.%s.indices.docs.deleted"),

    # STORE
    'indices.store.size': Stat("bytes", "nodes.%s.indices.store.size_in_bytes"),

    # INDEXING
    'indices.indexing.index-total': Stat("counter", "nodes.%s.indices.indexing.index_total"),
    'indices.indexing.index-time': Stat("counter", "nodes.%s.indices.indexing.index_time_in_millis"),
    'indices.indexing.delete-total': Stat("counter", "nodes.%s.indices.indexing.delete_total"),
    'indices.indexing.delete-time': Stat("counter", "nodes.%s.indices.indexing.delete_time_in_millis"),
    'indices.indexing.index-current': Stat("gauge", "nodes.%s.indices.indexing.index_current"),
    'indices.indexing.delete-current': Stat("gauge", "nodes.%s.indices.indexing.delete_current"),

    # GET
    'indices.get.total': Stat("counter", "nodes.%s.indices.get.total"),
    'indices.get.time': Stat("counter", "nodes.%s.indices.get.time_in_millis"),
    'indices.get.exists-total': Stat("counter", "nodes.%s.indices.get.exists_total"),
    'indices.get.exists-time': Stat("counter", "nodes.%s.indices.get.exists_time_in_millis"),
    'indices.get.missing-total': Stat("counter", "nodes.%s.indices.get.missing_total"),
    'indices.get.missing-time': Stat("counter", "nodes.%s.indices.get.missing_time_in_millis"),
    'indices.get.current': Stat("gauge", "nodes.%s.indices.get.current"),

    # SEARCH
    'indices.search.query-current': Stat("gauge", "nodes.%s.indices.search.query_current"),
    'indices.search.query-total': Stat("counter", "nodes.%s.indices.search.query_total"),
    'indices.search.query-time': Stat("counter", "nodes.%s.indices.search.query_time_in_millis"),
    'indices.search.fetch-current': Stat("gauge", "nodes.%s.indices.search.fetch_current"),
    'indices.search.fetch-total': Stat("counter", "nodes.%s.indices.search.fetch_total"),
    'indices.search.fetch-time': Stat("counter", "nodes.%s.indices.search.fetch_time_in_millis"),

    # JVM METRICS #
    # MEM
    'jvm.mem.heap-committed': Stat("bytes", "nodes.%s.jvm.mem.heap_committed_in_bytes"),
    'jvm.mem.heap-used': Stat("bytes", "nodes.%s.jvm.mem.heap_used_in_bytes"),
    'jvm.mem.heap-used-percent': Stat("percent", "nodes.%s.jvm.mem.heap_used_percent"),
    'jvm.mem.non-heap-committed': Stat("bytes", "nodes.%s.jvm.mem.non_heap_committed_in_bytes"),
    'jvm.mem.non-heap-used': Stat("bytes", "nodes.%s.jvm.mem.non_heap_used_in_bytes"),

    # THREADS
    'jvm.threads.count': Stat("gauge", "nodes.%s.jvm.threads.count"),
    'jvm.threads.peak': Stat("gauge", "nodes.%s.jvm.threads.peak_count"),

    # TRANSPORT METRICS #
    'transport.server_open': Stat("gauge", "nodes.%s.transport.server_open"),
    'transport.rx.count': Stat("counter", "nodes.%s.transport.rx_count"),
    'transport.rx.size': Stat("counter", "nodes.%s.transport.rx_size_in_bytes"),
    'transport.tx.count': Stat("counter", "nodes.%s.transport.tx_count"),
    'transport.tx.size': Stat("counter", "nodes.%s.transport.tx_size_in_bytes"),

    # HTTP METRICS #
    'http.current_open': Stat("gauge", "nodes.%s.http.current_open"),
    'http.total_open': Stat("counter", "nodes.%s.http.total_opened"),

    # PROCESS METRICS #
    'process.open_file_descriptors': Stat("gauge", "nodes.%s.process.open_file_descriptors"),
}

# ElasticSearch 1.3.0
INDEX_STATS_ES_1_3 = {
    # SEGMENTS
    "indices[index={index_name}].primaries.segments.index_writer_memory_in_bytes": Stat("bytes", "primaries.segments.index_writer_memory_in_bytes"),
    "indices[index={index_name}].primaries.segments.version_map_memory_in_bytes": Stat("bytes", "primaries.segments.version_map_memory_in_bytes"),
}

# ElasticSearch 1.1.0
INDEX_STATS_ES1_1 = {
    # SUGGEST
    "indices[index={index_name}].primaries.suggest.total": Stat("counter", "primaries.suggest.total"),
    "indices[index={index_name}].primaries.suggest.time_in_millis": Stat("counter", "primaries.suggest.time_in_millis"),
    "indices[index={index_name}].primaries.suggest.current": Stat("gauge", "primaries.suggest.current"),
}

# ElasticSearch 1.0.0
INDEX_STATS_ES1_0 = {
    # TRANSLOG
    "indices[index={index_name}].primaries.translog.size_in_bytes": Stat("bytes", "primaries.translog.size_in_bytes"),
    "indices[index={index_name}].primaries.translog.operations": Stat("counter", "primaries.translog.operations"),

    # SEGMENTS
    "indices[index={index_name}].primaries.segments.memory_in_bytes": Stat("bytes", "primaries.segments.memory_in_bytes"),
    "indices[index={index_name}].primaries.segments.count": Stat("counter", "primaries.segments.count"),

    # ID_CACHE
    "indices[index={index_name}].primaries.id_cache.memory_size_in_bytes": Stat("bytes", "primaries.id_cache.memory_size_in_bytes"),

    # FLUSH
    "indices[index={index_name}].primaries.flush.total": Stat("counter", "primaries.flush.total"),
    "indices[index={index_name}].primaries.flush.total_time_in_millis": Stat("counter", "primaries.flush.total_time_in_millis"),

    # WARMER
    "indices[index={index_name}].primaries.warmer.total.primaries.warmer.total_time_in_millis": Stat("counter", "primaries.warmer.total_time_in_millis"),
    "indices[index={index_name}].primaries.warmer.total": Stat("counter", "primaries.warmer.total"),
    "indices[index={index_name}].primaries.warmer.current": Stat("gauge", "primaries.warmer.current"),

    # FIELDDATA
    "indices[index={index_name}].primaries.fielddata.memory_size_in_bytes": Stat("bytes", "primaries.fielddata.memory_size_in_bytes"),
    "indices[index={index_name}].primaries.fielddata.evictions": Stat("counter", "primaries.fielddata.evictions"),

    # REFRESH
    "indices[index={index_name}].primaries.refresh.total_time_in_millis": Stat("counter", "primaries.refresh.total_time_in_millis"),
    "indices[index={index_name}].primaries.refresh.total": Stat("counter", "primaries.refresh.total"),

    # MERGES
    "indices[index={index_name}].primaries.merges.total_docs": Stat("counter", "primaries.merges.total_docs"),
    "indices[index={index_name}].primaries.merges.total_size_in_bytes": Stat("bytes", "primaries.merges.total_size_in_bytes"),
    "indices[index={index_name}].primaries.merges.current": Stat("gauge", "primaries.merges.current"),
    "indices[index={index_name}].primaries.merges.total": Stat("counter", "primaries.merges.total"),
    "indices[index={index_name}].primaries.merges.current_docs": Stat("gauge", "primaries.merges.current_docs"),
    "indices[index={index_name}].primaries.merges.total_time_in_millis": Stat("counter", "primaries.merges.total_time_in_millis"),
    "indices[index={index_name}].primaries.merges.current_size_in_bytes": Stat("bytes", "primaries.merges.current_size_in_bytes"),

    # COMPELTION
    "indices[index={index_name}].primaries.completion.size_in_bytes": Stat("bytes", "primaries.completion.size_in_bytes"),

    # PERCOLATE
    "indices[index={index_name}].primaries.percolate.total": Stat("counter", "primaries.percolate.total"),
    "indices[index={index_name}].primaries.percolate.memory_size_in_bytes": Stat("bytes", "primaries.percolate.memory_size_in_bytes"),
    "indices[index={index_name}].primaries.percolate.queries": Stat("counter", "primaries.percolate.queries"),
    "indices[index={index_name}].primaries.percolate.time_in_millis": Stat("counter", "primaries.percolate.time_in_millis"),
    "indices[index={index_name}].primaries.percolate.current": Stat("gauge", "primaries.percolate.current"),

    # FILTER_CACHE
    "indices[index={index_name}].primaries.filter_cache.evictions": Stat("counter", "primaries.filter_cache.evictions"),
    "indices[index={index_name}].primaries.filter_cache.memory_size_in_bytes": Stat("bytes", "primaries.filter_cache.memory_size_in_bytes"),
}

# DICT: Common index stats (0.9 and later)
INDEX_STATS = {
    # PRIMARIES
    # DOCS
    "indices[index={index_name}].primaries.docs.count": Stat("counter", "primaries.docs.count"),
    "indices[index={index_name}].primaries.docs.deleted": Stat("counter", "primaries.docs.deleted"),

    # STORE
    "indices[index={index_name}].primaries.store.size_in_bytes": Stat("bytes", "primaries.store.size_in_bytes"),
    "indices[index={index_name}].primaries.store.throttle_time_in_millis": Stat("counter", "primaries.store.throttle_time_in_millis"),

    # INDEXING
    "indices[index={index_name}].primaries.indexing.index_total": Stat("counter", "primaries.indexing.index_total"),
    "indices[index={index_name}].primaries.indexing.index_time_in_millis": Stat("counter", "primaries.indexing.index_time_in_millis"),
    "indices[index={index_name}].primaries.indexing.index_current": Stat("gauge", "primaries.indexing.index_current"),
    "indices[index={index_name}].primaries.indexing.delete_total": Stat("counter", "primaries.indexing.delete_total"),
    "indices[index={index_name}].primaries.indexing.delete_time_in_millis": Stat("counter", "primaries.indexing.delete_time_in_millis"),
    "indices[index={index_name}].primaries.indexing.delete_current": Stat("gauge", "primaries.indexing.delete_current"),

    # GET
    "indices[index={index_name}].primaries.get.time_in_millis": Stat("counter", "primaries.get.time_in_millis"),
    "indices[index={index_name}].primaries.get.exists_total": Stat("counter", "primaries.get.exists_total"),
    "indices[index={index_name}].primaries.get.exists_time_in_millis": Stat("counter", "primaries.get.exists_time_in_millis"),
    "indices[index={index_name}].primaries.get.missing_total": Stat("counter", "primaries.get.missing_total"),
    "indices[index={index_name}].primaries.get.missing_time_in_millis": Stat("counter", "primaries.get.missing_time_in_millis"),
    "indices[index={index_name}].primaries.get.current": Stat("gauge", "primaries.get.current"),

    # SEARCH
    "indices[index={index_name}].primaries.search.open_contexts": Stat("gauge", "primaries.search.open_contexts"),
    "indices[index={index_name}].primaries.search.query_total": Stat("counter", "primaries.search.query_total"),
    "indices[index={index_name}].primaries.search.query_time_in_millis": Stat("counter", "primaries.search.query_time_in_millis"),
    "indices[index={index_name}].primaries.search.query_current": Stat("gauge", "primaries.search.query_current"),
    "indices[index={index_name}].primaries.search.fetch_total": Stat("counter", "primaries.search.fetch_total"),
    "indices[index={index_name}].primaries.search.fetch_time_in_millis": Stat("counter", "primaries.search.fetch_time_in_millis"),
    "indices[index={index_name}].primaries.search.fetch_current": Stat("gauge", "primaries.search.fetch_current"),

    ## TOTAL ##
    # DOCS
    "indices[index={index_name}].total.docs.count": Stat("gauge", "total.docs.count"),
    "indices[index={index_name}].total.docs.deleted": Stat("gauge", "total.docs.deleted"),

    # STORE
    "indices[index={index_name}].total.store.size_in_bytes": Stat("gauge", "total.store.size_in_bytes"),
    "indices[index={index_name}].total.store.throttle_time_in_millis": Stat("counter", "total.store.throttle_time_in_millis"),

    # INDEXING
    "indices[index={index_name}].total.indexing.index_total": Stat("counter", "total.indexing.index_total"),
    "indices[index={index_name}].total.indexing.index_time_in_millis": Stat("counter", "total.indexing.index_time_in_millis"),
    "indices[index={index_name}].total.indexing.index_current": Stat("gauge", "total.indexing.index_current"),
    "indices[index={index_name}].total.indexing.delete_total": Stat("counter", "total.indexing.delete_total"),
    "indices[index={index_name}].total.indexing.delete_time_in_millis": Stat("counter", "total.indexing.delete_time_in_millis"),
    "indices[index={index_name}].total.indexing.delete_current": Stat("gauge", "total.indexing.delete_current"),

    # GET
    "indices[index={index_name}].total.get.total": Stat("counter", "total.get.total"),
    "indices[index={index_name}].total.get.time_in_millis": Stat("counter", "total.get.time_in_millis"),
    "indices[index={index_name}].total.get.exists_total": Stat("counter", "total.get.exists_total"),
    "indices[index={index_name}].total.get.exists_time_in_millis": Stat("counter", "total.get.exists_time_in_millis"),
    "indices[index={index_name}].total.get.missing_total": Stat("counter", "total.get.missing_total"),
    "indices[index={index_name}].total.get.missing_time_in_millis": Stat("counter", "total.get.missing_time_in_millis"),
    "indices[index={index_name}].total.get.current": Stat("gauge", "total.get.current"),

    # SEARCH
    "indices[index={index_name}].total.search.open_contexts": Stat("gauge", "total.search.open_contexts"),
    "indices[index={index_name}].total.search.query_total": Stat("counter", "total.search.query_total"),
    "indices[index={index_name}].total.search.query_time_in_millis": Stat("counter", "total.search.query_time_in_millis"),
    "indices[index={index_name}].total.search.query_current": Stat("gauge", "total.search.query_current"),
    "indices[index={index_name}].total.search.fetch_total": Stat("counter", "total.search.fetch_total"),
}

# ElasticSearch cluster stats (0.9.x and later)
CLUSTER_STATS = {
    'cluster.active_primary_shards': Stat("gauge", "cluster.%s.active_primary_shards"),
    'cluster.active_shards': Stat("gauge", "cluster.%s.active_shards"),
    'cluster.initializing_shards': Stat("gauge", "cluster.%s.initializing_shards"),
    'cluster.number_of_data_nodes': Stat("gauge", "cluster.%s.number_of_data_nodes"),
    'cluster.number_of_nodes': Stat("gauge", "cluster.%s.number_of_nodes"),
    'cluster.relocating_shards': Stat("gauge", "cluster.%s.relocating_shards"),
    'cluster.unassigned_shards': Stat("gauge", "cluster.%s.unassigned_shards"),
}

# collectd callbacks


def read_callback():
    """called by collectd to gather stats. It is called per collection interval.
    If this method throws, the plugin will be skipped for an increasing amount
    of time until it returns normally again"""
    log_verbose('Read callback called')
    fetch_stats()


def configure_callback(conf):
    """called by collectd to configure the plugin. This is called only once"""
    global ES_HOST, ES_PORT, ES_NODE_URL, ES_VERSION, VERBOSE_LOGGING, ES_CLUSTER, ES_INDEX, ENABLE_INDEX_STATS, ENABLE_CLUSTER_STATS
    for node in conf.children:
        if node.key == 'Host':
            ES_HOST = node.values[0]
        elif node.key == 'Port':
            ES_PORT = int(node.values[0])
        elif node.key == 'Verbose':
            VERBOSE_LOGGING = bool(node.values[0])
        elif node.key == 'Cluster':
            ES_CLUSTER = node.values[0]
        elif node.key == 'Version':
            ES_VERSION = node.values[0]
        elif node.key == 'Indexes':
            ES_INDEX = node.values
        elif node.key == 'EnableIndexStats':
            ENABLE_INDEX_STATS = bool(node.values[0])
        elif node.key == 'EnableClusterHealth':
            ENABLE_CLUSTER_STATS = bool(node.values[0])
        else:
            collectd.warning('elasticsearch plugin: Unknown config key: %s.'
                             % node.key)

    # intialize stats map based on ES version
    init_stats()


# helper methods
def init_stats():
    global ES_HOST, ES_PORT, ES_NODE_URL, ES_CLUSTER_URL, ES_INDEX_URL, ES_VERSION, VERBOSE_LOGGING, NODE_STATS_CUR, INDEX_STATS_CUR, CLUSTER_STATS_CUR, ENABLE_INDEX_STATS, ENABLE_CLUSTER_STATS
    if ES_VERSION.startswith("0."):
        # assume 0.9
        ES_NODE_URL = "http://" + ES_HOST + ":" + \
            str(ES_PORT) + "/_cluster/nodes/_local/stats?http=true&process=true&jvm=true&transport=true&thread_pool=true"
        NODE_STATS_CUR = dict(NODE_STATS.items() + NODE_STATS_ES09.items())
        INDEX_STATS_CUR = dict(INDEX_STATS)
    else:
        # 1.0 or higher
        ES_NODE_URL = "http://" + ES_HOST + ":" + \
            str(ES_PORT) + \
            "/_nodes/_local/stats/transport,http,process,jvm,indices,thread_pool"
        NODE_STATS_CUR = dict(NODE_STATS.items() + NODE_STATS_ES1.items())
        if ES_VERSION.startswith("1.0"):
            INDEX_STATS_CUR = INDEX_STATS
        elif ES_VERSION.startswith("1.1") or ES_VERSION.startswith("1.2"):
            INDEX_STATS_CUR = dict(
                INDEX_STATS.items() + INDEX_STATS_ES1_0.items())
        else:
            # 1.3 and higher
            INDEX_STATS_CUR = dict(
                INDEX_STATS.items() + INDEX_STATS_ES1_0.items() + INDEX_STATS_ES_1_3.items())

    # version agnostic settings
    if not ES_INDEX:
        # get all index stats
        ES_INDEX_URL = "http://" + ES_HOST + \
            ":" + str(ES_PORT) + "/_all/_stats"
    else:
        ES_INDEX_URL = "http://" + ES_HOST + ":" + \
            str(ES_PORT) + "/" + ",".join(ES_INDEX) + "/_stats"

    # add info on thread pools (applicable for all versions)
    for pool in ['generic', 'index', 'get', 'snapshot', 'merge', 'optimize',
                 'bulk', 'warmer', 'flush', 'search', 'refresh']:
        for attr in ['threads', 'queue', 'active', 'largest']:
            path = 'thread_pool.{0}.{1}'.format(pool, attr)
            NODE_STATS_CUR[path] = Stat("gauge", 'nodes.%s.{0}'.format(path))
        for attr in ['completed', 'rejected']:
            path = 'thread_pool.{0}.{1}'.format(pool, attr)
            NODE_STATS_CUR[path] = Stat("counter", 'nodes.%s.{0}'.format(path))

    ES_CLUSTER_URL = "http://" + ES_HOST + \
        ":" + str(ES_PORT) + "/_cluster/health"

    log_verbose('Configured with version=%s, host=%s, port=%s, url=%s' %
                (ES_VERSION, ES_HOST, ES_PORT, ES_NODE_URL))


# FUNCTION: Collect node stats from JSON result
def lookup_node_stat(stat, json):
    node = json['nodes'].keys()[0]
    val = dig_it_up(json, NODE_STATS_CUR[stat].path % node)

    # Check to make sure we have a valid result
    # dig_it_up returns False if no match found
    if not isinstance(val, bool):
        return int(val)
    else:
        return None


def fetch_stats():
    """
    fetches all required stats from ElasticSearch. This method also sets
    ES_CLUSTER
    """
    global ES_CLUSTER

    node_json_stats = fetch_url(ES_NODE_URL)
    ES_CLUSTER = node_json_stats['cluster_name']
    log_verbose('Configured with cluster_json_stats=%s' % ES_CLUSTER)
    parse_node_stats(node_json_stats, NODE_STATS_CUR)

    if ENABLE_CLUSTER_STATS:
        cluster_json_stats = fetch_url(ES_CLUSTER_URL)
        parse_cluster_stats(cluster_json_stats, CLUSTER_STATS)

    if ENABLE_INDEX_STATS:
        indexes_json_stats = fetch_url(ES_INDEX_URL)['indices']
        for index_name in indexes_json_stats.keys():
            parse_index_stats(indexes_json_stats[index_name], index_name)


def fetch_url(url):
    try:
        result = json.load(urllib2.urlopen(url, timeout=10))
    except urllib2.URLError, e:
        collectd.error(
            'elasticsearch plugin: Error connecting to %s - %r' % (url, e))
        return None
    return result


def parse_node_stats(json, stats):
    """Parse node stats response from ElasticSearch"""
    for name, key in stats.iteritems():
        result = lookup_node_stat(name, json)
        dispatch_stat(result, name, key)


def parse_cluster_stats(json, stats):
    """Parse cluster stats response from ElasticSearch"""
    for name, key in stats.iteritems():
        result = dig_it_up(json, name)
        dispatch_stat(result, name, key)


def parse_index_stats(json, index_name):
    """Parse index stats response from ElasticSearch"""
    for name, key in INDEX_STATS_CUR.iteritems():
        result = dig_it_up(json, key.path)
        # update the index name in the type_instance to include
        # the index as a dimensions
        name = name.format(index_name=sanitize_type_instance(index_name))
        dispatch_stat(result, name, key)


def sanitize_type_instance(index_name):
    """
    collectd limit the character set in type_instance to ascii and forbids
    the '/' character. This method does a lossy conversion to ascii and
    replaces the reserved character with '_'
    """
    ascii_index_name = index_name.encode('ascii', 'ignore')
    # '/' is reserved, so we substitute it with '_' instead
    return ascii_index_name.replace('/', '_')


def dispatch_stat(result, name, key):
    """Read a key from info response data and dispatch a value"""
    if result is None:
        collectd.warning('elasticsearch plugin: Value not found for %s' % name)
        return
    estype = key.type
    value = int(result)
    log_verbose('Sending value[%s]: %s=%s' % (estype, name, value))

    val = collectd.Values(plugin='elasticsearch')
    val.plugin_instance = ES_CLUSTER
    val.type = estype
    val.type_instance = name
    val.values = [value]
    val.meta = {'0': True}
    val.dispatch()


def dig_it_up(obj, path):
    try:
        if type(path) in (str, unicode):
            path = path.split('.')
        return reduce(lambda x, y: x[y], path, obj)
    except:
        return False


def log_verbose(msg):
    if not VERBOSE_LOGGING:
        return
    collectd.info('elasticsearch plugin [verbose]: %s' % msg)


# The following classes are there to launch the plugin manually
# with something like ./elasticsearch_collectd.py for development
# purposes. They basically mock the calls on the "collectd" symbol
# so everything prints to stdout.
class CollectdMock(object):

    def __init__(self):
        self.value_mock = CollectdValuesMock

    def error(self, msg):
        print 'ERROR: {}'.format(msg)
        sys.exit(1)

    def Values(self, plugin='elasticsearch'):
        return (self.value_mock)()


class CollectdValuesMock(object):

    def dispatch(self):
        print self

    def __str__(self):
        attrs = []
        for name in dir(self):
            if not name.startswith('_') and name is not 'dispatch':
                attrs.append("{}={}".format(name, getattr(self, name)))
        return "<CollectdValues {}>".format(' '.join(attrs))

if __name__ == '__main__':
    import sys
    collectd = CollectdMock()
    init_stats()
    fetch_stats()
else:
    import collectd
    collectd.register_config(configure_callback)
    collectd.register_read(read_callback)
