import threading

from flask import *
import pandas as pd
from flask import render_template
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import numpy as np
import base64

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        dis = request.form['dist']
        return redirect(url_for('.plot_png', messages=dis))
    else:

        df = pd.read_csv("https://api.covid19india.org/csv/latest/districts.csv")
        districts =set(df["District"])
        districts=list(districts)
        districts=sorted(districts)
        messages= districts[0]
        return render_template('index.html', dist=districts)
def post(self):
    dis = self.request.get('d')
    return redirect(url_for('.plot_png', messages=dis))
@app.route('/plot',methods=['GET', 'POST'])
def plot_png():
    disname=request.args['messages']
    fig = create_figure(disname)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')
def create_figure(x):
    data = pd.read_csv("https://api.covid19india.org/csv/latest/districts.csv")
    data.rename(columns={'Confirmed': 'Total Confirmed',
                         'Recovered': 'Total Recovered',
                         'Deceased': 'Total Deceased'},
                inplace=True)
    data['Date'] = pd.to_datetime(data['Date'])
    dist = data.loc[data.District == x]
    T1 = dist['Total Confirmed']
    an = 6
    reminder = (len(T1) % an)
    if reminder != 0:
        T1 = T1[0:-reminder]
    re = ((len(T1)) // an)
    Week = range(0, re)
    T1 = T1.to_numpy()
    T1 = T1.reshape(re, an)
    double = []
    print(len(T1))
    for n in range(0, len(T1)):
        l2 = np.log(2)
        Diff = np.log(T1[n][an - 1] / T1[n][0])
        V = l2 * (an - 1) / Diff
        double.append(V)
    WL = dist['Date']
    WL = WL[6::an]
    DRate = pd.DataFrame(list(zip(double, Week, WL)),
                         columns=['DRate', 'Weeks', 'Date'])
    fig = Figure(figsize = (18, 6))
    axis = fig.add_subplot(1, 1, 1)
    img = io.BytesIO()
    date= DRate['Date']
    l=len(DRate)
    d=str(date[l-1])
    da=date
    ys = DRate['DRate']
    labels= np.round_(ys)
    xs = DRate['Weeks']
    axis.set_xlabel('Weeks')
    axis.set_ylabel('Doubling Rate')
    axis.set_title('Doubling Rate of '+ x + ' until '+ d)
    axis.bar(xs, ys)
    for i, v in enumerate(labels):
        axis.text(i - .090,
                  v / labels[i] + 00,
                  labels[i],
                  fontsize=10,)
                  #color=label_color_list[i])
    return fig

if __name__ == "__main__":
    app.run(debug=True)
