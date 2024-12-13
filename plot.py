import math
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import pathlib

RESULTS_DIR = "./results"
OUT_DIR = "./figures"


def load_data(file):
    df = pd.read_csv(file, sep=',')
    df = df[["timeStamp", "responseCode"]]
    df = df.sort_values(by=["timeStamp"])
    return df


def group_data(df):
    def set_key(key, df):
        if key in df:
            df[key] = df[key].map(
                lambda x: (0.0 if math.isnan(x) else 334 if x > 334 else x))
        else:
            df[key] = 0
        return df

    first_time = df["timeStamp"].iloc[0]

    # Get seconds elapsed since start
    df["timeStamp"] = df["timeStamp"].map(lambda t: (t - first_time) // 1000)
    df = df.value_counts(sort=False).unstack().reset_index()

    df = set_key(200, df)
    df = set_key(500, df)

    return df


def plot_data(df):
    print(df)
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.bar(df["timeStamp"], df[200], label="Success", width=1.0)
    ax.bar(df["timeStamp"], df[500], label="Failure", width=1.0)

    ax.set_ylabel("requests pr. second")
    ax.set_xlabel("seconds")

    ax.legend(labels=["Success", "Failure"])
    plt.ylim((0, 334))
    plt.xlim(0)

    # df.plot(x="timeStamp", y="count", kind="bar")
    # plt.show()


def save_fig(name):
    filename = name.split("/")[-1]
    newname = filename[0:-4] + ".png"
    plt.savefig(f"{OUT_DIR}/{newname}")


if __name__ == "__main__":
    pathlib.Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
    results = pathlib.Path(RESULTS_DIR).glob("*.csv")
    for result in results:
        df = load_data(result)
        df = group_data(df)
        plot_data(df)
        save_fig(str(result))
