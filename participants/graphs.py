
import datetime as dt
import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from io import BytesIO
from .models import Participant

def _setup_figure():
    """Setup the figure and axis for a default graph with 1 subplot"""
    fig = Figure(figsize=(10,8), dpi=200)
    canvas = FigureCanvasAgg(fig)
    return fig

def diff_months(d1 :dt.date, d2 :dt.date):
    """ thanks: https://stackoverflow.com/a/4040338/2082884"""
    return (d1.year - d2.year) * 12 + d1.month - d2.month


def render_demograhpics():
    """Renders default graph for /participants/demographics"""

    fig = _setup_figure()
    ax = fig.add_subplot()

    qset = Participant.objects.all()

    today = dt.date.today()
    delta_months = [diff_months(today, pp.birth_date) for pp in qset]

    num_bins= max(delta_months) - min(delta_months) + 10
    
    ax.hist(delta_months, bins=num_bins)
    ax.set_xlabel("Age in months")
    ax.set_ylabel("Number of observations")

    payload = BytesIO()

    color = (9/10, 9/10, 9/10)

    fig.savefig(payload, facecolor=color)
    payload.seek(0)

    return payload.read(-1)
