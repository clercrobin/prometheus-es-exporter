from collections import OrderedDict


def parse_buckets(agg_key, buckets, metric=None, labels=None):
    if metric is None:
        metric = []
    if labels is None:
        labels = OrderedDict()

    result = []

    for index, bucket in enumerate(buckets):
        labels_next = labels.copy()

        if 'key' in bucket.keys():
            bucket_key = str(bucket['key'])
            if agg_key in labels_next.keys():
                labels_next[agg_key] = labels_next[agg_key] + [bucket_key]
            else:
                labels_next[agg_key] = [bucket_key]
            del bucket['key']
        else:
            bucket_key = 'filter_' + str(index)
            if agg_key in labels_next.keys():
                labels_next[agg_key] = labels_next[agg_key] + [bucket_key]
            else:
                labels_next[agg_key] = [bucket_key]

        result.extend(parse_agg(bucket_key, bucket, metric=metric, labels=labels_next))

    return result


def parse_buckets_fixed(agg_key, buckets, metric=None, labels=None):
    if metric is None:
        metric = []
    if labels is None:
        labels = OrderedDict()

    result = []

    for bucket_key, bucket in buckets.items():
        labels_next = labels.copy()

        if agg_key in labels_next.keys():
            labels_next[agg_key] = labels_next[agg_key] + [bucket_key]
        else:
            labels_next[agg_key] = [bucket_key]

        result.extend(parse_agg(bucket_key, bucket, metric=metric, labels=labels_next))

    return result


def parse_agg(agg_key, agg, metric=None, labels=None):
    f=open("/var/tmp/prometheus_insight.txt", "a+")
    print("Beginning of parseagg", file=f)
    if metric is None:
        metric = []
    if labels is None:
        labels = OrderedDict()

    result = []
    if agg_key:
        print("agg_key", file=f)
        print(agg_key, file=f)
    if agg:
        print("agg", file=f)
        print(agg, file=f)
    if metric:
        print("metric", file=f)
        print(metric, file=f)
    if labels:
        print("labels", file=f)
        print(labels, file=f)

    for key, value in agg.items():
        print("\n", file=f)
        print(key, file=f)
        print("\n", file=f)
        print(value, file=f)
        if key == 'buckets' and isinstance(value, list):
            print("inlistbucket", file=f)
            result.extend(parse_buckets(agg_key, value, metric=metric, labels=labels))
        elif key == 'buckets' and isinstance(value, dict):
            print("indictbucket", file=f)
            result.extend(parse_buckets_fixed(agg_key, value, metric=metric, labels=labels))
        elif isinstance(value, dict):
            print("indict", file=f)
            result.extend(parse_agg(key, value, metric=metric + [key], labels=labels))
        else:
            print("else", file=f)
            result.append((metric + [key], labels, value))
    print("End of parseagg", file=f)
    f.close()
    return result


def parse_response(response, metric=None):
    f=open("/var/tmp/prometheus_insight.txt", "a+")
    print("Repsponse and metrics", file=f)
    print(response, file=f)
    print(metric, file = f)
    print("Beginning of the new response", file=f)
    if metric is None:
        metric = []

    result = []

    if not response['timed_out']:
        result.append((metric + ['hits'], {}, response['hits']['total']))
        result.append((metric + ['took', 'milliseconds'], {}, response['took']))

        if 'aggregations' in response.keys():
            for key, value in response['aggregations'].items():
                print(key, file=f)
                print(value, file=f)
                result.extend(parse_agg(key, value, metric=metric + [key]))
    print("End of the response", file=f)
    f.close()
    return result
