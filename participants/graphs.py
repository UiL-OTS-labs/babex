
from .models import Participant
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from io import BytesIO

def render_demograhpics():
    """Renders default graph for /participants/demographics"""
    fig = Figure(figsize=(16,9), dpi=100)

    canvas = FigureCanvasAgg(fig)
    ax = fig.add_subplot()
    ax.plot([i*i - 15 for i in  range(-10, 11, 1)])

    payload = BytesIO()

    color = (9/10, 9/10, 9/10)

    fig.savefig(payload, facecolor=color)
    payload.seek(0)

    return payload.read(-1)
