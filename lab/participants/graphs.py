import datetime as dt
from io import BytesIO
from typing import List

import matplotlib.axes
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from .models import Participant


def _setup_figure(width, height):
    """Setup the figure and axis for a default graph with 1 subplot"""
    desired_dpi = 100
    fig = Figure(figsize=(width // desired_dpi, height // desired_dpi), dpi=desired_dpi)
    _ = FigureCanvasAgg(fig)

    return fig


def diff_months(d1: dt.date, d2: dt.date):
    """thanks: https://stackoverflow.com/a/4040338/2082884"""

    return (d1.year - d2.year) * 12 + d1.month - d2.month


def render_all_participants(ax: matplotlib.axes.SubplotBase, participants: List[Participant], today):
    """Render demographics for all participants"""
    delta_months = [diff_months(today, pp.birth_date) for pp in participants]

    num_bins = max(delta_months) - min(delta_months) + 10

    ax.hist(delta_months, bins=num_bins)
    ax.set_xlabel("Current age (months)")
    ax.set_ylabel("Number of participants")


def render_participants_by_group(ax: matplotlib.axes.SubplotBase, participants: List[Participant], today):
    """Split the participants into groups, and create histogram."""
    delta_months = [diff_months(today, pp.birth_date) for pp in participants]
    num_bins = max(delta_months) - min(delta_months) + 10

    risc_dyslexia = [pp for pp in participants if pp.dyslexic_parent not in (None, Participant.WhichParent.NEITHER)]
    multilingual = [pp for pp in participants if pp.multilingual]
    premature = [pp for pp in participants if pp.pregnancy_duration == Participant.PregnancyDuration.LESS_THAN_37]
    rest = [pp for pp in participants if pp not in set(risc_dyslexia + multilingual + premature)]

    delta_dys = [diff_months(today, pp.birth_date) for pp in risc_dyslexia]
    delta_mult = [diff_months(today, pp.birth_date) for pp in multilingual]
    delta_premature = [diff_months(today, pp.birth_date) for pp in premature]
    delta_rest = [diff_months(today, pp.birth_date) for pp in rest]

    ax.hist(
        [delta_dys, delta_mult, delta_premature, delta_rest],
        bins=num_bins,
        histtype="bar",
        label=["Parent with Dyslexia", "Multilingual", "Premature", "Other"],
    )
    ax.legend(loc="upper right")
    ax.set_xlabel("Current age (months)")
    ax.set_ylabel("Number of participants")


def render_demograhpics(width: int, height: int) -> bytes:
    """Renders default graph for /participants/demographics"""

    today = dt.date.today()
    fig = _setup_figure(width, height)

    participants = Participant.objects.filter(deactivated=None)
    ax_pp = fig.subplots()

    render_all_participants(ax_pp, list(participants), today)

    payload = BytesIO()
    fig.savefig(payload, transparent=False, format="svg")
    payload.seek(0)
    return payload.read(-1)


def render_demograhpics_by_group(width: int, height: int) -> bytes:
    """Renders default graph for /participants/demographics"""

    today = dt.date.today()
    fig = _setup_figure(width, height)

    participants = Participant.objects.filter(deactivated=None)
    ax_group = fig.subplots()

    render_participants_by_group(ax_group, list(participants), today)

    payload = BytesIO()

    fig.savefig(payload, transparent=False, format="svg")
    payload.seek(0)

    return payload.read(-1)
