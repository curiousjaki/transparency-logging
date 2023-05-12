<source>
  @type tail
  read_from_head true
  tag tilt.*
  path /var/log/containers/*.log
  pos_file /var/log/fluentd-containers.log.pos
  exclude_path ["/var/log/containers/fluent*"]
  <parse>
    @type json
    time_key time:timestamp
    time_type string
    time_format "%Y-%m-%d %H:%M:%S,%3N"
  </parse> 
</source>
<filter tilt.**>
  @type grep
  <regexp>
    key log
    pattern /\"tilt\":/
  </regexp>
</filter>

<match tilt.**>
  @type elasticsearch
  host "#{ENV['FLUENT_ELASTICSEARCH_HOST'] || 'elasticsearch.elastic-kibana'}"
  port "#{ENV['FLUENT_ELASTICSEARCH_PORT'] || '9200'}"
  index_name fluentd-k8s
  type_name fluentd
  include_timestamp true
</match>