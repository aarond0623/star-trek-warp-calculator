#!/usr/bin/env python3

from __future__ import division, print_function
import sys
import tkinter as tk
from tkinter import ttk


def warp_to_c(warp, digits=15, tos=False):
    """
    Converts a warp factor to a lightspeed factor using the Berry-Shields
    equation from Dominic Berry and Martin Shields for warp factors above 9.
    Namely:

    f(w) = w^(10/3) for warp factors less than or equal to 9, and
    g(w) = f(w) * w^(e^(-1/(B(w - 9)^2)) * A * (-ln(10 - w)) ^ N) for w > 9

    where B is a constant that determines the shape of the curve,
    A = 0.03658749373, and
    N = 1.7952294708
    """
    from math import exp, log
    wf = (10/3)
    if tos:
        wf = 3.0
    try:
        warp = float(warp)
    except (ValueError, TypeError) as err:
        print("ERROR: argument must be a real number.")
        print("%s: %s" % (type(err).__name__, err))
        return
    # Handle negative warp values.
    try:
        multiplier = warp / abs(warp)
    except ZeroDivisionError:
        return 0
    warp = abs(warp)

    if warp >= 10 and not tos:
        return float('inf')
    lightspeed = warp ** wf
    if warp > 9 and not tos:
        A = 0.03658749373
        N = 1.7952294708
        B = 1000
        lightspeed *= warp ** (exp(-1/(B * (warp - 9)**2)) *
                               A * (-log(10 - warp))**N)
    return round(multiplier * lightspeed, digits)


def c_to_warp(lightspeed, digits=15, tos=False, accur=15):
    """
    Does the opposite of warp_to_c by using roots if under 9 and estimating
    through Newton's method if over 9 in order to calculate warp.
    """
    wf = 3/10
    if tos:
        wf = 1/3
    try:
        lightspeed = float(lightspeed)
    except (ValueError, TypeError) as err:
        print("ERROR: argument must be a real number.")
        print("%s: %s" % (type(err).__name__, err))
        return
    # Handle negative speeds.
    try:
        multiplier = lightspeed / abs(lightspeed)
    except ZeroDivisionError:
        return 0
    lightspeed = abs(lightspeed)
    if lightspeed <= 9 ** (10/3) or tos:
        return round(multiplier * lightspeed ** wf, digits)
    else:
        warp = 9
        decimal = 0.1
        while (abs(warp_to_c(warp, accur) - lightspeed) > 10**(-accur) and
               warp + decimal != warp):
            if warp_to_c(warp, accur) < lightspeed:
                warp += decimal
            elif warp_to_c(warp, accur) > lightspeed:
                warp -= decimal
                decimal /= 10
                warp += decimal
            else:
                break
        decimal *= 10
        if (abs(warp_to_c(warp + decimal, 15) - lightspeed) <
                abs(warp_to_c(warp, 15) - lightspeed)):
            warp += decimal
        return round(multiplier * warp, digits)


def eta(distance, warp, tos=False, accur=15, month_use=True, week_use=True):
    """
    Calculates the time need to travel a certain distance at warp.
    """
    try:
        distance = float(distance)
        warp = float(warp)
    except (ValueError, TypeError) as err:
        print("ERROR: arguments must be real numbers.")
        print("%s: %s" % (type(err).__name__, err))
        return
    lightspeed = warp_to_c(warp, accur, tos)
    try:
        time = distance / lightspeed
        print(time_to_text(time, month_use, week_use))
        return time
    except ZeroDivisionError:
        return float('nan')


def min_warp(distance, time=None, digits=15, tos=False):
    """
    Calculates the warp factor needed to travel a certain distance in a certain
    amount of time.
    """
    try:
        distance = float(distance)
    except (ValueError, TypeError) as err:
        print("ERROR: distance must be a real number.")
        print("%s: %s" % (type(err).__name__, err))
        return
    if time == None:
        print("Enter time to destination.")
        while True:
            try:
                years = float(input("  Years: "))
                days = float(input("   Days: "))
                hours = float(input("  Hours: "))
                minutes = float(input("Minutes: "))
                seconds = float(input("Seconds: "))
                break
            except (ValueError, TypeError) as err:
                print("ERROR: time values must be real numbers.")
                print("%s: %s" % (type(err).__name__, err))
        time = (years + days/365.2425 + hours / (365.2425*24) +
                minutes/(365.2425*24*60) + seconds/(365.2425*24*3600))
    try:
        lightspeed = distance / time
        return c_to_warp(lightspeed, digits, tos)
    except (ValueError, TypeError) as err:
        print("ERROR: time must be a real number.")
        print("%s: %s" % (type(err).__name__, err))
        return


def max_dist(warp, time=None, digits=15, tos=False):
    """
    Calculates the maximum distance that can be traveled at a warp factor over
    some time.
    """
    try:
        warp = float(warp)
    except (ValueError, TypeError) as err:
        print("ERROR: warp must be a real number.")
        print("%s: %s" % (type(err).__name__, err))
        return
    if time == None:
        print("Enter time to destination.")
        while True:
            try:
                years = float(input("  Years: "))
                days = float(input("   Days: "))
                hours = float(input("  Hours: "))
                minutes = float(input("Minutes: "))
                seconds = float(input("Seconds: "))
                break
            except (ValueError, TypeError) as err:
                print("ERROR: time values must be real numbers.")
                print("%s: %s" % (type(err).__name__, err))
        time = (years + days/365.2425 + hours / (365.2425*24) +
                minutes/(365.2425*24*60) + seconds/(365.2425*24*3600))
    speed = warp_to_c(warp, digits, tos)
    try:
        distance = speed * time
        return round(distance, digits)
    except (ValueError, TypeError) as err:
        print("ERROR: time must be a real number.")
        print("%s: %s" % (type(err).__name__, err))
        return


def time_to_text(time, month_use=True, week_use=True):
    years = str(int(time))
    time -= int(years)

    if month_use:
        months = str(int(time * 12))
        time -= int(months) / 12
    else:
        months = str(0)

    if week_use:
        weeks = str(int(time * (365.2425 / 7)))
        time -= int(weeks) / (365.2425 / 7)
    else:
        weeks = str(0)

    days = str(int(time * 365.2425))
    time -= int(days) / 365.2425
    hours = str(int(time * 365.2425 * 24))
    time -= int(hours) / (365.2425 * 24)
    minutes = str(int(time * 365.2425 * 24 * 60))
    time -= int(minutes) / (365.2425 * 24 * 60)
    seconds = str(int(time * 365.2425 * 24 * 60 * 60 * 100) / 100)

    if years == "1":
        years += " year "
    elif years == "0":
        years = ""
    else:
        years += " years "

    if months == "1":
        months += " month "
    elif months == "0":
        months = ""
    else:
        months += " months "

    if weeks == "1":
        weeks += " week "
    elif weeks == "0":
        weeks = ""
    else:
        weeks += " weeks "

    if days == "1":
        days += " day "
    elif days == "0":
        days = ""
    else:
        days += " days "

    if hours == "1":
        hours += " hour "
    elif hours == "0":
        hours = ""
    else:
        hours += " hours "

    if minutes == "1":
        minutes += " minute "
    elif minutes == "0":
        minutes = ""
    else:
        minutes += " minutes "

    if seconds == "1":
        seconds += " second"
    elif seconds == "0" or seconds == "0.0":
        seconds = ""
    else:
        seconds += " seconds"

    return(years + months + weeks + days + hours + minutes + seconds)


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        style = ttk.Style()
        style.map("C.TButton",
            foreground=[('pressed', 'red'), ('active', 'blue')],
            background=[('pressed', '!disabled', 'black'),
                          ('active', 'white')]
            )
        self.parent = parent

        self.digits = 3

        tk.Label(self.parent, text="Warp Factor:").grid(row=0, column=0)
        self.warp = tk.StringVar()
        self._warp = tk.Entry(self.parent, textvariable=self.warp)
        self._warp.grid(row=0, column=1)
        self.tos_values = {"TNG": False, "TOS": True}
        self.tos = tk.StringVar()
        self._tos = ttk.OptionMenu(self.parent, self.tos,
                                  "TNG",
                                  *self.tos_values.keys())
        self._tos.config(width=7)
        self._tos.grid(row=0, column=2)

        tk.Label(self.parent, text="Speed:").grid(row=1, column=0)
        self.lightspeed = tk.StringVar()
        self._lightspeed = tk.Entry(self.parent, textvariable=self.lightspeed)
        self._lightspeed.grid(row=1, column=1)
        self.speed_values = {"Speed of Light (c)": 1, "km/s": 299792.458}
        self.speed = tk.StringVar()
        self._speed = ttk.OptionMenu(self.parent, self.speed,
                                    "Speed of Light (c)",
                                    *self.speed_values.keys())
        self._speed.config(width=15)
        self._speed.grid(row=1, column=2)

        tk.Label(self.parent, text="Time:").grid(row=2, column=0)
        self.time = tk.StringVar()
        self._time = tk.Entry(self.parent, textvariable=self.time)
        self._time.grid(row=2, column=1)
        self.t_unit_values = {"Years": 1,
                              "Months": 12,
                              "Weeks": (365.2425 / 7),
                              "Days": 365.2425,
                              "Hours": (365.2425 * 24),
                              "Minutes": (365.2425 * 24 * 60),
                              "Seconds": (365.2425 * 24 * 60 * 60)}
        self.t_unit = tk.StringVar()
        self._t_unit = ttk.OptionMenu(self.parent, self.t_unit,
                                        "Days",
                                        *self.t_unit_values.keys())
        self._t_unit.config(width=8)
        self._t_unit.grid(row=2, column=2)

        tk.Label(self.parent, text="Distance:").grid(row=3, column=0)
        self.distance = tk.StringVar()
        self._distance = tk.Entry(self.parent, textvariable=self.distance)
        self._distance.grid(row=3, column=1)
        self.d_unit_values = {"Parsecs": 0.306601,
                              "Lightyears": 1,
                              "AU": 63241.08,
                              "Kilometers": 9460730777119.56}
        self.d_unit = tk.StringVar()
        self._d_unit = ttk.OptionMenu(self.parent, self.d_unit,
                                     "Lightyears",
                                     *self.d_unit_values.keys())
        self._d_unit.config(width=10)
        self._d_unit.grid(row=3, column=2)

        tk.Label(self.parent, text="Calculate:").grid(row=4, column=0)
        self.choice_values = {"Warp Factor": self.c_to_warp,
                              "Speed": self.warp_to_c,
                              "Time": self.eta,
                              "Distance": self.max_dist,
                              "Required Warp": self.min_warp}
        self.choice = tk.StringVar()
        self._choice = ttk.OptionMenu(self.parent, self.choice,
                                     "Speed",
                                     *self.choice_values.keys())
        self._choice.config(width=13)
        self._choice.grid(row=4, column=1)

        self._submit = ttk.Button(self.parent, text="Submit",
                                 command=self.submit)
        self._submit.grid(row=4, column=2)

    def submit(self):
        self.choice_values[self.choice.get()]()

    def warp_to_c(self):
        tos = self.tos_values[self.tos.get()]
        speed = self.speed_values[self.speed.get()]
        self.lightspeed.set(round(warp_to_c(self.warp.get(), 15, tos) * speed, self.digits))

    def c_to_warp(self):
        tos = self.tos_values[self.tos.get()]
        speed = self.speed_values[self.speed.get()]
        self.warp.set(round(c_to_warp(float(self.lightspeed.get()) / speed, 15, tos), self.digits))

    def eta(self):
        tos = self.tos_values[self.tos.get()]
        speed = self.speed_values[self.speed.get()]
        t_unit = self.t_unit_values[self.t_unit.get()]
        d_unit = self.d_unit_values[self.d_unit.get()]
        try:
            w = float(self.warp.get())
        except (ValueError, TypeError):
            w = c_to_warp(float(self.lightspeed.get()) / speed, 15, tos)
        self.time.set(round(eta(float(self.distance.get()) / d_unit, w, tos) * t_unit, self.digits))

    def max_dist(self):
        tos = self.tos_values[self.tos.get()]
        speed = self.speed_values[self.speed.get()]
        t_unit = self.t_unit_values[self.t_unit.get()]
        d_unit = self.d_unit_values[self.d_unit.get()]
        try:
            w = float(self.warp.get())
        except (ValueError, TypeError):
            w = c_to_warp(float(self.lightspeed.get()) / speed, 15, tos)
        self.distance.set(round(max_dist(w, float(self.time.get()) / t_unit, 15, tos) * d_unit, self.digits))

    def min_warp(self):
        tos = self.tos_values[self.tos.get()]
        speed = self.speed_values[self.speed.get()]
        t_unit = self.t_unit_values[self.t_unit.get()]
        d_unit = self.d_unit_values[self.d_unit.get()]
        self.warp.set(round(min_warp(float(self.distance.get()) / d_unit, float(self.time.get()) / t_unit, 15, tos), self.digits))


if __name__ == '__main__':
    root = tk.Tk()

    root.wm_title("Warp Calculator")
    MainApplication(root)

    root.mainloop()
