import altair as alt


def prepare_chart(df, columns_mapper):
    # Prepares DataFrame `df` for charting using alt.Chart().
    #
    # Altair doesn't use the index, so we move it into columns. Then columns are
    # renamed according to the `columns_mapper` dict. (This is necessary because
    # Altair doesn't work well with verbose column names, and it doesn't support
    # multi-level columns anyway.) Columns that don't appear in the dict are
    # dropped.
    #
    # Note: contrary to DataFrame.rename(), in the case of MultiIndex columns,
    # `columns_mapper` keys are matched against the full column name (i.e. a
    # tuple), not individual per-level labels.
    df = df.reset_index().loc[:, list(columns_mapper.keys())]
    df.columns = df.columns.map(mapper=columns_mapper)
    return df


def interactive_line(chart, legend_channel):
    # Note that `legend_channel` should explicitly override the legend
    # symbolType to 'stroke', otherwise it gets set to 'circle' from the hidden
    # layer, which is wrong. A clear way to avoid this problem would be to make
    # the legends independent and disable the legend on the hidden layer, but
    # that causes problems with faceted charts, see:
    #   https://github.com/vega/vega-lite/issues/6261

    mouseover_selection = alt.selection_single(on='mouseover', empty='none')
    legend_selection = alt.selection_multi(encodings=['color'], bind='legend')
    # This is equivalent to using the `point` line mark property.
    # The reason why we don't simply do that is because tooltips wouldn't work
    # as well due to this Vega-lite bug:
    #   https://github.com/vega/vega-lite/issues/6107
    return alt.layer(
        # Note: order is important. If the points chart comes first, legend selection doesn't work.
        chart
        .mark_line(clip=True, interpolate='monotone')
        .add_selection(legend_selection)
        .encode(
            legend_channel,
            opacity=alt.condition(
                legend_selection, alt.value(1), alt.value(0.2))
        ),
        chart
        .mark_circle(clip=True, size=100)
        .add_selection(mouseover_selection)
        .encode(
            # We don't use legend_selection for points. If we do, it seems to
            # break legend interactivity in weird ways on non-faceted charts.
            legend_channel,
            fillOpacity=alt.condition(
                mouseover_selection, alt.value(0.3), alt.value(0)))
        .interactive())