from .construction import Construction
import pandas as pd
import matplotlib.pyplot as plt


def plot_bar_chart_comparison(structures: list[Construction],
                               latex: bool = False) -> plt.Axes:
    """
    Make a bar plot comparasion. Resulting data are a little scaled
    due to very different values.

    https://stackoverflow.com/questions/14270391/python-matplotlib-multiple-bars
    """
    names = [struct.name for struct in structures]
    data = [struct.create_dict_valuable_properties() for struct in structures]

    df = pd.DataFrame(data, index=names)

    # Since numbers to compare are very different, we "scale" values.
    df["surface mass"] = df["surface mass"] / 100
    # periodischer Wärmedurchgangskoeffizient
    df["|Y12|"] = df["|Y12|"] * 100
    # daempfungsfaktor
    df["decrement factor"] = df["decrement factor"] * 10
    # innere waermekapazitaet
    df["internal area heat capacity"] = df["internal area heat capacity"] / 10

    ax = df.plot(
        kind="bar", rot=0, xlabel="Pareti", title="Comparison", figsize=(6, 4)
    )

    # Add some labels.
    for c in ax.containers:
        # set the bar label
        ax.bar_label(c, fmt="%.2f", label_type="edge")

    # Add a little space at the top of the plot for the annotation.
    ax.margins(y=0.5)

    if latex:
        custom_labels = [
            "$d_{tot}$ [m]",
            "R [m$^2$ K W$^{-1}$]",
            "m' [$\\times10^2$ kg m$^{-2}$]",
            "$|Y_{12}|$ [$\\times10^{-2}$ W m$^{-2}$ K$^{-1}$]",
            "$\varphi$ [h]",
            "f [$\\times10^{-1}$]",
            "$\kappa_1$ [$\\times10^{1}$ kJ m$^{-2}$ K$^{-1}$]",
        ]
    else:
        custom_labels = [
            "d_tot [m]",
            "R [m2 K W-1]",
            "m' [100 * kg m-1]",
            "|Y12| [0.01 *  W m-2 K-1]",
            "phi [h]",
            "f [* 0.1]",
            "k1 [10 * kJ m-2 K-1]",
        ]
    ax.legend(loc="upper center", labels=custom_labels, frameon=True, ncol=2)

    return ax
