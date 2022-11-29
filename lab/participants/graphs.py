
import datetime as dt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import matplotlib.axes
from io import BytesIO
from typing import List
from .models import Participant


def _setup_figure(width, height):
    """Setup the figure and axis for a default graph with 1 subplot"""
    desired_dpi = 100
    fig = Figure(
        figsize=(width // desired_dpi, height // desired_dpi),
        dpi=desired_dpi
    )
    _ = FigureCanvasAgg(fig)

    return fig


def diff_months(d1: dt.date, d2: dt.date):
    """ thanks: https://stackoverflow.com/a/4040338/2082884"""

    return (d1.year - d2.year) * 12 + d1.month - d2.month


def render_all_participants(
        ax: matplotlib.axes.SubplotBase,
        participants: List[Participant],
        today):
    '''Render demographics for all participants'''
    delta_months = [diff_months(today, pp.birth_date) for pp in participants]

    num_bins = max(delta_months) - min(delta_months) + 10

    ax.hist(delta_months, bins=num_bins)
    ax.set_xlabel("Age in months")
    ax.set_ylabel("Number of observations")


def render_participants_by_group(
        ax: matplotlib.axes.SubplotBase,
        participants: List[Participant],
        today):
    """Split the participants into groups, and create histogram."""
    delta_months = [diff_months(today, pp.birth_date) for pp in participants]
    num_bins = max(delta_months) - min(delta_months) + 10

    risc_dyslexia = [pp for pp in participants if pp.dyslexic_parent]
    multilingual = [pp for pp in participants if pp.multilingual]
    premature = [pp for pp in participants if pp.pregnancy_weeks <= 37]

    colors = ["red", "blue", "green"]

    delta_dys = [diff_months(today, pp.birth_date) for pp in risc_dyslexia]
    delta_mult = [diff_months(today, pp.birth_date) for pp in multilingual]
    delta_premature = [diff_months(today, pp.birth_date) for pp in premature]

    ax.hist(
        [delta_dys, delta_mult, delta_premature],
        bins=num_bins,
        histtype='bar',
        color=colors,
        label=["Dyslexic parent", "Multilingual", "Premature"]
    )
    ax.legend(loc='upper right')


def render_demograhpics(width: int, height: int, img_format: str):
    """Renders default graph for /participants/demographics"""
    print(f"width = {width}, height={height}, format={img_format}")

    today = dt.date.today()
    fig = _setup_figure(width, height)

    participants = Participant.objects.all()
    ax_pp = fig.add_subplot(2, 1, 1)
    ax_group = fig.add_subplot(2, 1, 2, sharex=ax_pp, sharey=ax_pp)

    render_all_participants(ax_pp, list(participants), today)
    render_participants_by_group(ax_group, list(participants), today)

    payload = BytesIO()

    fig.savefig(payload, transparent=False, format=img_format)
    payload.seek(0)

    return payload.read(-1)
