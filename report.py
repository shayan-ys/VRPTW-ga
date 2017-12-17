import ga_params
if ga_params.draw_plot:
    import matplotlib.pyplot as plt
if ga_params.export_spreadsheet:
    from openpyxl import Workbook
from datetime import datetime
import re


class Reporter:

    plot_x_axis = []
    plot_y_axis = []
    sheet_wb = None
    sheet_ws = None
    sheet_dest = 'output'
    sheet_dest_ext = '.xlsx'

    def __init__(self, run_name: str):
        if ga_params.draw_plot:
            plt.ion()
            self.fig, self.subplot = plt.subplots()
            self.fig_node_connector, self.subplot2 = plt.subplots()
        if ga_params.export_spreadsheet:
            self.init_spreadsheet(run_name=run_name)

    def plot_draw(self, x_axis: list, y_axis: list, latest_result):
        y_axis_parsed = []
        for y in y_axis:
            try:
                y_axis_parsed.append(y['best'])
            except:
                break
        if y_axis_parsed:
            y_axis = y_axis_parsed

        plt.figure(1)
        # self.subplot.set_xlim([self.plot_x_axis[0], self.plot_x_axis[-1]])
        self.subplot.set_ylim([min(y_axis) - 5, max(y_axis) + 5])
        plt.suptitle('Best solution so far: ' + re.sub("(.{64})", "\\1\n", str(latest_result), 0, re.DOTALL),
                     fontsize=10)
        print(latest_result)
        self.subplot.plot(x_axis, y_axis)

        plt.figure(2)
        for route_x, route_y in latest_result.plot_get_route_cords():
            plt.plot(route_x, route_y)

        plt.draw()
        self.fig.savefig("plot-output.png")
        self.fig_node_connector.savefig("plot2-output.png")
        plt.pause(0.000001)

    def init_spreadsheet(self, run_name: str):
        datetime_str = datetime.now().strftime('%b%d-%H:%M')
        # datetime_str = '1'
        self.sheet_dest = self.sheet_dest + '_' + run_name + '_' + datetime_str + self.sheet_dest_ext
        self.sheet_wb = Workbook()
        self.sheet_ws = self.sheet_wb.active
        self.sheet_ws.append(['gen_index', 'best', 'average', 'std', 'worst', 'created_time', 'computation_time',
                              'best_route'])

    def export_spreadsheet(self, x_axis: list, y_axis: list):

        datetime_str = str(datetime.now())
        
        for x, y in zip(x_axis, y_axis):
            self.sheet_ws.append([x, y['best'].value, y['average'], y['std'], y['worst'].value, datetime_str,
                                  str(y['process_time']), str(y['best'].route)])

        # Save the file
        self.sheet_wb.save(filename=self.sheet_dest)
