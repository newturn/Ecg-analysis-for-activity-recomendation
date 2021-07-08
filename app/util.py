# -*- coding: utf-8 -*-
import typing as t
from functools import wraps

import neurokit2 as nk
import pandas as pd
from flask import flash, redirect, url_for
import numpy as np

from app import app


def check_expired(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            if kwargs['key'] != app.secret_key:
                flash("You can't be here yet")
                return redirect(url_for('upload'))
        except IndexError:
            flash("You can't be here yet")
            return redirect(url_for('upload'))
        return func(*args, **kwargs)
    return decorated_function


def calc_rs_peaks(ecg_signal: pd.Series) -> t.Tuple[float, float]:
    # ecg_signal = np.diff(ecg_signal)
    ecg_clean = nk.ecg_clean(ecg_signal, sampling_rate=1000)
    _, rpeaks = nk.ecg_peaks(ecg_clean, sampling_rate=1000)
    rpeaks: np.array = rpeaks['ECG_R_Peaks']
    rpeaks = rpeaks[~(np.isnan(rpeaks))]  # drop na values
    # Delineate the ECG signal
    _, waves_peak = nk.ecg_delineate(ecg_clean, rpeaks, sampling_rate=1000)
    speaks: np.array = np.array(waves_peak['ECG_S_Peaks'])
    speaks = speaks[~(np.isnan(speaks))]
    # return mean of R & S peaks
    rpeak_avg = abs(ecg_clean[rpeaks].mean())
    speaks_avg = abs(ecg_clean[speaks].mean())
    return rpeak_avg, speaks_avg


def calc_rs_sum(r_peak: float, s_peak: float) -> float:
    return r_peak / (r_peak + s_peak) * 100


def calc_aerobic_power(RS_6: t.Tuple[float, float]) -> float:
    return (RS_6[0] - 100/(RS_6[0] + RS_6[1])) * 100


def calc_w_and_heart_rate_pano(V_2: t.Tuple[float, float], V_6: t.Tuple[float, float]) -> t.Tuple[float, float]:
    V_2_calc = calc_rs_sum(V_2[0], V_2[1])
    V_6_calc = calc_rs_sum(V_6[0], V_6[1])
    W_pano = calc_rs_sum(V_6_calc, V_2_calc)  # метаболическая мощность
    HR_pano = sum([V_2_calc, V_6_calc, W_pano])  # ЧССпано
    return W_pano, HR_pano


def calc_metabolic_capacity(V_2: t.Tuple[float, float], V_3R: t.Tuple[float, float],
                            V_6: t.Tuple[float, float]) -> float:
    return calc_rs_sum(V_2[0], V_2[1]) + calc_rs_sum(V_3R[0], V_3R[1])\
            + calc_rs_sum(V_6[0], V_6[1]) + calc_w_and_heart_rate_pano(V_2, V_6)[0]


def calc_max_lactate_storage(V_2: t.Tuple[float, float]) -> float:
    return 2.8 * calc_rs_sum(V_2[0], V_2[1]) + 4.06


def calc_max_lactate_storage_after_work(V_2: t.Tuple[float, float]) -> float:
    return calc_rs_sum(V_2[0], V_2[1]) / 3


def calc_max_creatine_phosphate_consumption(V_3R: t.Tuple[float, float]) -> float:
    return calc_rs_sum(V_3R[0], V_3R[1])


def calc_restorability():
    """
    Данный параметр измеряется на динамике: 3 мин, 30 мин, 2, 4, 12, 24, 48 часов
    для всех трех отведений, после прекращения мышечной работы любого типа.

    При этом увеличение отношения R / R+S в соответствующих отведениях ΔЭКГ в послерабочем
    периоде более чем на 10 % означает наступление фазы суперкомпенсации,
    последующее его понижение больше 10% знаменует развитие фазы сниженной работоспособности.
    """
    pass


def cals_ability():
    """
    Данный показатель оценивают путем вычисления процента отклонения текущих величин отношения
    R*100 / R+S в каждом из трех отведений ΔЭКГ покоя (V3R , V2, Vб) и производных
    показателей от модельных значений, характерных для атлетов высшей квалификации
    """
    pass
