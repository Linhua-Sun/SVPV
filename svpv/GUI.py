# # -*- coding: utf-8 -*-
# """
# @author: j.munro@victorchang.edu.au
#
# """

import Tkinter as tk
import GUI_Widgets as gw
from plot import Plot


class SVPVGui(tk.Tk):
    def __init__(self, par):
        tk.Tk.__init__(self)
        self.par = par
        self.option_add("*Font", "arial 10")

        self.buttons_1 = None
        self.reset = None
        self.list = None
        self.buttons_2 = None
        self.viewGTs = None
        self.viewSV = None
        self.setup_static_features()

        self.config(menu=gw.MenuBar(self))
        self.current_samples = []
        self.svs = self.par.run.vcf.filter_svs(self.par.filter, as_list=True)
        self.sample_selector = None
        self.set_sample_selector()
        self.genotype_selector = None
        self.set_genotype_selector()
        self.filters = None
        self.set_filters()
        self.sv_chooser = None
        self.set_sv_chooser()
        self.info_box = None
        self.set_info_box()

        self.filename = None

    def setup_static_features(self):
        self.wm_title("SVPV - Structural Variant Prediction Viewer")
        self.window_size()

        if self.buttons_1:
            self.buttons_1.destroy()
        self.buttons_1 = tk.LabelFrame(self)
        if self.reset:
            self.reset.destroy()
        self.reset = tk.Button(self.buttons_1, text="Reset Filters", command=self.reset)
        self.reset.grid(row=0, column=0, padx=40, sticky=tk.W)
        if self.list:
            self.list.destroy()
        self.list = tk.Button(self.buttons_1, text="Apply Filters", command=self.apply_filters)
        self.list.grid(row=0, column=1, padx=40, sticky=tk.E)
        self.buttons_1.grid(row=3, column=0, columnspan=2, sticky=tk.EW, padx=10)

        if self.buttons_2:
            self.buttons_2.destroy()
        self.buttons_2 = tk.LabelFrame(self)
        if self.viewGTs:
            self.viewGTs.destroy()
        self.viewGTs = tk.Button(self.buttons_2, text="Get Genotypes", command=self.view_gts)
        self.viewGTs.grid(row=0, column=0, padx=40, sticky=tk.W)
        if self.viewSV:
            self.viewSV.destroy()
        self.viewSV = tk.Button(self.buttons_2, text="View Structural Variant", command=self.view_sv)
        self.viewSV.grid(row=0, column=1, padx=40, sticky=tk.E)
        self.buttons_2.grid(row=5, column=0, columnspan=2, sticky=tk.EW, padx=10)

    def text_size(self, opt):
        if opt == 1:
            self.option_add("*Font", "arial 8")
        elif opt == 2:
            self.option_add("*Font", "arial 10")
        elif opt == 3:
            self.option_add("*Font", "arial 12")
        elif opt == 4:
            self.option_add("*Font", "arial 14")
        elif opt == 5:
            self.option_add("*Font", "arial 16")
        self.setup_static_features()
        self.set_sample_selector()
        self.set_genotype_selector()
        self.set_filters()
        self.set_sv_chooser()
        self.set_info_box()

    def set_sample_selector(self):
        if self.sample_selector:
            self.sample_selector.destroy()
        self.sample_selector = gw.SampleSelector(self, self.par.run.samples)
        self.sample_selector.grid(row=1, column=0, sticky=tk.NSEW, padx=10)

    def set_genotype_selector(self):
        if self.genotype_selector:
            self.genotype_selector.destroy()
        self.genotype_selector = gw.SampleGenotypeSelector(self, self.current_samples)
        self.genotype_selector.grid(row=1, column=1, sticky=tk.NSEW, padx=10)

    def set_filters(self):
        if self.filters:
            self.filters.destroy()
        self.filters = gw.Filters(self)
        self.filters.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW, pady=2, padx=10)

    def set_sv_chooser(self):
        if self.sv_chooser:
            self.sv_chooser.destroy()
        self.sv_chooser = gw.SvChooser(self, self.svs, self.par.run.vcf.count)
        self.sv_chooser.grid(row=4, column=0, sticky=tk.NSEW, padx=10, columnspan=2)

    def set_info_box(self, message=''):
        self.info_box = gw.InfoBox(self, message)
        self.info_box.grid(row=6, column=0, sticky=tk.NSEW, padx=10, columnspan=2)

    def reset(self):
        self.current_samples = []
        self.set_genotype_selector()
        self.filters.reset()
        self.apply_filters()
        self.set_sv_chooser()

    def view_gts(self):
        self.info_box.genotypes(self.svs[self.sv_chooser.sv_fl.selected_idx], self.par.run.vcf.samples, self.par.run.samples)

    def apply_filters(self):
        self.par.filter.sample_GTs = {}
        if self.genotype_selector.GT_CBs:
            for i, gt_cb in enumerate(self.genotype_selector.GT_CBs):
                if gt_cb.get_selection():
                    self.par.filter.sample_GTs[self.genotype_selector.samples[i]] = gt_cb.get_selection()
        else:
            self.par.filter.GTs = ['*']

        # update af filter
        self.par.filter.AF_thresh = None
        if self.filters.af_filter.af_on.get():
            self.par.filter.AF_thresh = self.filters.af_filter.af_var.get()
            if self.filters.af_filter.af_gt_lt.get() == 1:
                self.par.filter.AF_thresh_is_LT = True
            else:
                self.par.filter.AF_thresh_is_LT = False

        # update gene_list_intersection
        self.par.filter.gene_list_intersection = False
        if self.filters.gene_filter.gene_list_on.get():
            self.par.filter.gene_list_intersection = True

        # update ref_gene_intersection
        self.par.filter.RG_intersection = False
        if self.filters.gene_filter.ref_gene_on.get():
            self.par.filter.RG_intersection = True

        # update exonic
        self.par.filter.exonic = False
        if self.filters.gene_filter.exonic_on.get():
            self.par.filter.exonic = True

        # update length filter
        self.par.filter.max_len = None
        self.par.filter.min_len = None
        if self.filters.len_filter.len_GT_On.get():
            units = 1
            if str(self.filters.len_filter.len_GT_Units.get()) == 'kbp':
                units = 1000
            elif str(self.filters.len_filter.len_GT_Units.get()) == 'Mbp':
                units = 1000000
            self.par.filter.min_len = units * int(self.filters.len_filter.len_GT_val.get())
        if self.filters.len_filter.len_LT_On.get():
            units = 1
            if str(self.filters.len_filter.len_LT_Units.get()) == 'kbp':
                units = 1000
            elif str(self.filters.len_filter.len_LT_Units.get()) == 'Mbp':
                units = 1000000
            self.par.filter.max_len = units * int(self.filters.len_filter.len_LT_val.get())

        #update svtype filter
        self.par.filter.svtype = None
        if self.filters.type_filter.type_var.get():
            val = self.filters.type_filter.type_var.get()
            if val == 1:
                self.par.filter.svtype = 'DEL'
            elif val == 2:
                self.par.filter.svtype = 'DUP'
            elif val == 3:
                self.par.filter.svtype = 'CNV'
            elif val == 4:
                self.par.filter.svtype = 'INV'

        # get list of svs based on current filters
        self.svs = self.par.run.vcf.filter_svs(self.par.filter, as_list=True)
        self.set_sv_chooser()

    def view_sv(self):
        if not self.current_samples:
            self.info_box.message.config(text="Error: No Samples Selected")
        else:
            plot = Plot(self.svs[self.sv_chooser.sv_fl.selected_idx], self.current_samples, self.par)
            self.filename = plot.plot_figure()

    def window_size(self):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = int(0.05 * sw)
        y = int(0.05 * sh)
        self.geometry('+%d+%d' % (x, y))

    def samples_update(self, idxs):
        self.current_samples = []
        for idx in idxs:
            self.current_samples.append(self.par.run.samples[idx])
        self.genotype_selector.destroy()
        self.genotype_selector = gw.SampleGenotypeSelector(self, self.current_samples)
        self.genotype_selector.grid(row=1, column=1, sticky=tk.NSEW, padx=10)


def main(par):
    root = SVPVGui(par)
    root.mainloop()

