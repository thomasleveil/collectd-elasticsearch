### CHANGELOG

This file documents important changes to the Elasticsearch plugin for collectd. 

- [2016-07-21: Dimensionalize thread pool metrics
by thread pool](#2016-07-21-dimensionalize-thread-pool-metrics-by-thread-pool)
- [2016-06-28: Basic configuration
changes](#2016-06-28-changes-to-basic-plugin-configuration) 
- [2016-06-27: Support for basic 
authentication](#2016-06-27-support-for-basic-authentication)

#### 2016-07-21: Dimensionalize thread pool metrics by thread pool

Prior to this update, the plugin transmitted thread pool metrics with the names
of thread pools as part of the name.

Ex. (Where thread_pool is "search")
```
counter.thread_pool.search.rejected
```

This update removes the name of the thread pool from the metric name and 
attaches attaches the thread pool as a dimension named "thread_pool". 

Ex. (Where thread_pool is "search")
```Bash
counter.thread_pool.rejected
# The metric above now has the dimension 
# named "thread_pool" set to "search"
```

*Custom dashboards and detectors will need to be updated to monitor 
based on the new metric names.*

#### 2016-06-28: Changes to basic plugin configuration

##### Control level of metrics detail

Before this update, the plugin transmitted every metric available from
Elasticsearch's stats API. Available metrics are now segmented into two sets:
"default", a curated set of metrics used in SignalFx's built-in dashboards for
this plugin, and "detailed" which includes all available metrics. Control the
set of metrics that will be transmitted in the `DetailedMetrics` configuration
parameter. To capture additional metrics beyond those in the default set without
enabling DetailedMetrics, use the `AdditionalMetrics` configuration parameter. 

`DetailedMetrics` is evaluated before `EnableIndexStats` and
`EnableClusterStats`. If `DetailedMetrics` is false, setting `EnableIndexStats`
and `EnableClusterStats` to true will cause the plugin to report only those
index and cluster metrics that are included in the default set of metrics.

##### Specify secondary collection interval for index stats

This update includes a separate collection interval for index stats, specified
in `IndexInterval`. This was added because the collection of index stats in
particular can be CPU-intensive. The default setting of this interval in
[`20-elasticsearch.conf`](https://github.com/signalfx/integrations/tree/master/collectd-elasticsearch/20-elasticsearch.conf) transmits index stats every 5 minutes. 

##### Address missing metric mappings in recent versions of Elasticsearch

This update adds compatibility with more recent versions of Elasticsearch up to
2.1, in which some metric names have changed. Before this update, the plugin
would log errors that metrics could not be found. 

#### 2016-06-27: Support for basic authentication 

The plugin was updated to support basic authentication with Elasticsearch
installations. You can now supply username and password in the configuration
file for this plugin. 
