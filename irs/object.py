"""IRS object to calculate the IRS for a given year using the IRS table in the
data folder. 
"""
from pathlib import Path
from datetime import date

import pandas as pd


IAS = 438.81 * 12 * 0.72


class IRS:
    """The object itself that allows adding previous and expected gains.

    Examples
    -------
    >>> person = IRS()
    >>> person.add_previous_values_cat_a(10000, 2000)
    >>> person.add_expected_values_cat_b(1500, 0.2)
    >>> person.calculate_irs_payable()
    -1041.86
    >>> another = IRS()
    >>> another.add_previous_values_cat_b(10000,3000)
    >>> together = person + another
    """
    def __init__(self):
        self.tabela = pd.read_excel(Path(__file__).parent / "data" / "tabela_irs.xlsx")
        self.leftover_months = 13 - date.today().month
        self.total_irs_deducted = 0
        self.number_of_people = 1
        self.total_gained_cat_b = 0
        self.total_gained_cat_a = 0

    def __add__(self, other):
        new_irs = IRS()
        new_irs.total_irs_deducted = self.total_irs_deducted + other.total_irs_deducted
        new_irs.total_gained_cat_a = self.total_gained_cat_a + other.total_gained_cat_a
        new_irs.total_gained_cat_b = self.total_gained_cat_b + other.total_gained_cat_b
        new_irs.number_of_people = self.number_of_people + 1
        return new_irs

    def add_previous_values_cat_a(self, previously_gained, previously_deducted):
        self.total_gained_cat_a += previously_gained
        self.total_irs_deducted += previously_deducted

    def add_expected_values_cat_a(self, monthly_gain, irs_deduction_perc):
        expected_gain = monthly_gain * self.leftover_months
        self.total_gained_cat_a += expected_gain
        self.total_irs_deducted += expected_gain * irs_deduction_perc

    def add_previous_values_cat_b(self, previously_gained, previously_deducted):
        self.total_gained_cat_b += previously_gained
        self.total_irs_deducted += previously_deducted

    def add_expected_values_cat_b(self, monthly_gain, irs_deduction_perc):
        expected_gain = monthly_gain * self.leftover_months
        self.total_gained_cat_b += expected_gain
        self.total_irs_deducted += expected_gain * irs_deduction_perc

    def calculate_irs_payable(self):
        self.total_irs_deductible = max(self.total_gained_cat_a - (IAS*self.number_of_people), 0) + 0.75 * self.total_gained_cat_b
        self.total_irs_deductible = self.total_irs_deductible / self.number_of_people
        ix = self.tabela[self.tabela["Maximo"]<self.total_irs_deductible].index[-1]
        med_tx = self.tabela.iloc[ix,-1]
        max_at_med_tx = self.tabela.iloc[ix,1]
        rest_tx = self.tabela.iloc[ix+1,-2]
        self.payable_irs = med_tx * max_at_med_tx + rest_tx * (self.total_irs_deductible - max_at_med_tx)
        self.payable_irs *= self.number_of_people
        return round(self.payable_irs - self.total_irs_deducted,2)
    
