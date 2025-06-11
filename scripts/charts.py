import matplotlib.pyplot as plt
import numpy as np

def generate_comparison_hist_chart(
        latency_range,
        count_range,
        data_dict,
        output_path,
        figsize = None,
        y_in_thousands = False,
        ):
    fig, axs = plt.subplots(len(data_dict), 1, sharex=True, figsize=figsize)
    fig.subplots_adjust(hspace=0)

    axis_ranges = [
        latency_range[0], latency_range[1],
        count_range[0], count_range[1]
    ]

    hist_bins = np.linspace(latency_range[0], latency_range[1], num=200)

    for i, (key, result) in enumerate(data_dict.items()):
        print(f"Calculating stats for {key}...")
        mean = np.mean(result)
        median = np.median(result)
        std = np.std(result)
        min = np.min(result)
        max = np.max(result)
        latency_outliers = (
            len(np.where(np.asarray(result) < latency_range[0])[0]),
            len(np.where(np.asarray(result) > latency_range[1])[0])
        )

        axs[i].grid(alpha=0.3)
        axs[i].axis(axis_ranges)
        axs[i].axvline(x=median, color='r', linestyle='--')
        axs[i].hist(result, bins=hist_bins, label = key)
        axs[i].scatter(max, 0, marker='x') #label = "Najwyższe odnotowane opóźnienie"
        axs[i].legend()
        if(y_in_thousands):
            axs[i].yaxis.set_major_formatter(lambda x, pos: round(x/1000, 2))
        axs[i].yaxis.get_major_ticks()[0].set_visible(False) # Hide the 0 tick so it doesn't overlap

        print(f"Stats for {key} ========================")
        print(f"Did not plot every entry for {key}:")
        print(f"Too-small outliers: {latency_outliers[0]} ({(latency_outliers[0] / len(result))*100}%)")
        print(f"Too-big outliers: {latency_outliers[1]} ({(latency_outliers[1] / len(result))*100}%)")
        print(f"mean: {mean*1000000} microseconds")
        print(f"median: {median*1000000} microseconds")
        print(f"std: {std*1000000} microseconds")
        print(f"max: {max*1000000} microseconds")
        print(f"min: {min*1000000} microseconds")

    last_ax = axs[len(axs)-1]
    last_ax.xaxis.set_major_formatter(lambda x, pos: round(x*1000000, 2))
    last_ax.yaxis.get_major_ticks()[0].set_visible(True)

    fig.text(0.5, 0.03, r'Opóźnienia [${\mu}s$]', ha='center')
    y_text = 'Zaobserwowane wywołania funkcji'
    if y_in_thousands:
        y_text = 'Zaobserwowane wywołania funkcji [w tysiącach]'
    fig.text(0.01, 0.5, y_text, va='center', rotation='vertical')

    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")
