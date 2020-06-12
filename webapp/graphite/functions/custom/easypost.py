import sys

from graphite.functions import ParamTypes, Param
from graphite.render.functions import normalize
from graphite.render.datalib import TimeSeries

if sys.version_info < (3, 0):
    from itertools import izip
else:
    izip = zip


def consecutiveNonZero(requestContext, *seriesLists):
    """
    Takes one metric or a wildcard seriesList.

    Output is the number of consecutive buckets for which at least one point in the
    series was non-zero. An explicit 0 resets the count; a null just does nothing.

    Example:

    .. code-block:: none

    &target=consecutiveNonZero(lb1.haproxy.frontend.queue_length)
    """

    seriesLists, start, end, step = normalize(seriesLists)

    name = 'consecutiveNonZero(%s)' % ','.join(s.name for s in seriesLists)
    count = 0
    result_values = []
    for values in izip(*seriesLists):
        if any(v is not None and v > 0 for v in values):
            count += 1
        elif any(v == 0 for v in values):
            count = 0
    result_values.append(count)
    resultSeries = TimeSeries(name, start, end, step, result_values)
    resultSeries.pathExpression = name
    return [ resultSeries ]


consecutiveNonZero.group = 'Transform'
consecutiveNonZero.params = [
    Param('seriesList', ParamTypes.seriesList, required=True),
]


def consecutiveSecondsNonZero(requestContext, *seriesLists):
    """
    Takes one metric or a wildcard seriesList.

    Output is the number of consecutive seconds for which at least one point in the
    series was non-zero. An explicit 0 resets the count; a null just does nothing.

    Example:

    .. code-block:: none

    &target=consecutiveSecondsNonZero(lb1.haproxy.frontend.queue_length)
    """

    seriesLists, start, end, step = normalize(seriesLists)

    name = 'consecutiveSecondsNonZero(%s)' % ','.join(s.name for s in seriesLists)
    value = 0
    result_values = []
    for i, values in enumerate(izip(*seriesLists)):
        if any(v is not None and v > 0 for v in values):
            value += step
        elif any(v == 0 for v in values):
            value = 0
    # if v is None, then leave value at its previous, uh, value
    result_values.append(value)
    resultSeries = TimeSeries(name, start, end, step, result_values)
    resultSeries.pathExpression = name
    return [ resultSeries ]


consecutiveSecondsNonZero.group = 'Transform'
consecutiveSecondsNonZero.params = [
    Param('seriesList', ParamTypes.seriesList, required=True),
]


def transformBelowValue(requestContext, seriesList, valueLimit, newValue):
    """
    Takes one metric or a wildcard seriesList.

    For every point below (valueLimit), replace it with (newValue). Does nothing
    to NULLs
    """

    for series in seriesList:
        series.tags['transformBelowValue'] = valueLimit
        series.tags['transformBelowValueNewValue'] = newValue
        series.name = "transformBelowValue(%s,%g,%g)" % (series.name, valueLimit, newValue)
        series.pathExpression = series.name
        values = [newValue if ( v is not None and v < valueLimit ) else v for v in series]
        series[:len(series)] = values
    return seriesList


transformBelowValue.group = 'Transform'
transformBelowValue.params = [
    Param('seriesList', ParamTypes.seriesList, required=True),
    Param('valueLimit', ParamTypes.float, required=True),
    Param('newValue', ParamTypes.float, required=True),
]


SeriesFunctions = {
    'consecutiveNonZero': consecutiveNonZero,
    'consecutiveSecondsNonZero': consecutiveSecondsNonZero,
    'consecutive': consecutiveSecondsNonZero,
    'transformBelowValue': transformBelowValue,
}

# I refuse to use upstream's non-PEP8 style
#
# vim: set ts=4 sw=4 sts=0 expandtab:
