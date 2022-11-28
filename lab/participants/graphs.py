
import datetime as dt
import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from io import BytesIO
from .models import Participant


def _setup_figure(width, height):
    """Setup the figure and axis for a default graph with 1 subplot"""
    desired_dpi = 100
    fig = Figure(
        figsize=(width // desired_dpi, height // desired_dpi),
        dpi=desired_dpi
    )
    canvas = FigureCanvasAgg(fig)
    return fig


def diff_months(d1: dt.date, d2: dt.date):
    """ thanks: https://stackoverflow.com/a/4040338/2082884"""
    return (d1.year - d2.year) * 12 + d1.month - d2.month


def render_demograhpics(width: int, height: int, img_format: str):
    """Renders default graph for /participants/demographics"""
    print(f"width = {width}, height={height}, format={img_format}")

    fig = _setup_figure(width, height)
    ax = fig.add_subplot()

    qset = Participant.objects.all()

    today = dt.date.today()
    delta_months = [diff_months(today, pp.birth_date) for pp in qset]

    num_bins = max(delta_months) - min(delta_months) + 10

    ax.hist(delta_months, bins=num_bins)
    ax.set_xlabel("Age in months")
    ax.set_ylabel("Number of observations")

    payload = BytesIO()

    fig.savefig(payload, transparent=False, format=img_format)
    payload.seek(0)

    return payload.read(-1)
