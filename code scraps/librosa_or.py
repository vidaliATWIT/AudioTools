#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Core IO, DSP and utility functions."""
from __future__ import annotations
import librosa
import os
import pathlib
import warnings

import soundfile as sf
import audioread
import numpy as np
import scipy.signal
import soxr
#import lazy_loader as lazy

from .. import util


from typing import Any, BinaryIO, Callable, Generator, Optional, Tuple, Union, List
from numpy.typing import DTypeLike, ArrayLike

# Lazy-load optional dependencies
#amplerate = lazy.load("samplerate")
#resampy = lazy.load("resampy")

__all__ = [
    "load",
    "stream",
    "to_mono",
    "resample",
    "get_duration",
    "get_samplerate",
    "autocorrelate",
    "lpc",
    "zero_crossings",
    "clicks",
    "tone",
    "chirp",
    "mu_compress",
    "mu_expand",
]

#from .._cache import cache

#@cache(level=20)
def resample(
    y: np.ndarray,
    *,
    orig_sr: float,
    target_sr: float,
    res_type: str = "soxr_hq",
    fix: bool = True,
    scale: bool = False,
    axis: int = -1,
    **kwargs: Any,
) -> np.ndarray:
    """Resample a time series from orig_sr to target_sr

    By default, this uses a high-quality method (`soxr_hq`) for band-limited sinc
    interpolation. The alternate ``res_type`` values listed below offer different
    trade-offs of speed and quality.

    Parameters
    ----------
    y : np.ndarray [shape=(..., n, ...)]
        audio time series, with `n` samples along the specified axis.

    orig_sr : number > 0 [scalar]
        original sampling rate of ``y``

    target_sr : number > 0 [scalar]
        target sampling rate

    res_type : str (default: `soxr_hq`)
        resample type

        'soxr_vhq', 'soxr_hq', 'soxr_mq' or 'soxr_lq'
            `soxr` Very high-, High-, Medium-, Low-quality FFT-based bandlimited interpolation.
            ``'soxr_hq'`` is the default setting of `soxr`.
        'soxr_qq'
            `soxr` Quick cubic interpolation (very fast, but not bandlimited)
        'kaiser_best'
            `resampy` high-quality mode
        'kaiser_fast'
            `resampy` faster method
        'fft' or 'scipy'
            `scipy.signal.resample` Fourier method.
        'polyphase'
            `scipy.signal.resample_poly` polyphase filtering. (fast)
        'linear'
            `samplerate` linear interpolation. (very fast, but not bandlimited)
        'zero_order_hold'
            `samplerate` repeat the last value between samples. (very fast, but not bandlimited)
        'sinc_best', 'sinc_medium' or 'sinc_fastest'
            `samplerate` high-, medium-, and low-quality bandlimited sinc interpolation.

        .. note::
            Not all options yield a bandlimited interpolator. If you use `soxr_qq`, `polyphase`,
            `linear`, or `zero_order_hold`, you need to be aware of possible aliasing effects.

        .. note::
            `samplerate` and `resampy` are not installed with `librosa`.
            To use `samplerate` or `resampy`, they should be installed manually::

                $ pip install samplerate
                $ pip install resampy

        .. note::
            When using ``res_type='polyphase'``, only integer sampling rates are
            supported.

    fix : bool
        adjust the length of the resampled signal to be of size exactly
        ``ceil(target_sr * len(y) / orig_sr)``

    scale : bool
        Scale the resampled signal so that ``y`` and ``y_hat`` have approximately
        equal total energy.

    axis : int
        The target axis along which to resample.  Defaults to the trailing axis.

    **kwargs : additional keyword arguments
        If ``fix==True``, additional keyword arguments to pass to
        `librosa.util.fix_length`.

    Returns
    -------
    y_hat : np.ndarray [shape=(..., n * target_sr / orig_sr, ...)]
        ``y`` resampled from ``orig_sr`` to ``target_sr`` along the target axis

    Raises
    ------
    ParameterError
        If ``res_type='polyphase'`` and ``orig_sr`` or ``target_sr`` are not both
        integer-valued.

    See Also
    --------
    librosa.util.fix_length
    scipy.signal.resample
    resampy
    samplerate.converters.resample
    soxr.resample

    Notes
    -----
    This function caches at level 20.

    Examples
    --------
    Downsample from 22 KHz to 8 KHz

    >>> y, sr = librosa.load(librosa.ex('trumpet'), sr=22050)
    >>> y_8k = librosa.resample(y, orig_sr=sr, target_sr=8000)
    >>> y.shape, y_8k.shape
    ((117601,), (42668,))
    """

    # First, validate the audio buffer
    util.valid_audio(y, mono=False)

    if orig_sr == target_sr:
        return y

    ratio = float(target_sr) / orig_sr

    n_samples = int(np.ceil(y.shape[axis] * ratio))

    if res_type in ("scipy", "fft"):
        y_hat = scipy.signal.resample(y, n_samples, axis=axis)
    elif res_type == "polyphase":
        if int(orig_sr) != orig_sr or int(target_sr) != target_sr:
            raise ParameterError(
                "polyphase resampling is only supported for integer-valued sampling rates."
            )

        # For polyphase resampling, we need up- and down-sampling ratios
        # We can get those from the greatest common divisor of the rates
        # as long as the rates are integrable
        orig_sr = int(orig_sr)
        target_sr = int(target_sr)
        gcd = np.gcd(orig_sr, target_sr)
        y_hat = scipy.signal.resample_poly(
            y, target_sr // gcd, orig_sr // gcd, axis=axis
        )
    elif res_type in (
        "linear",
        "zero_order_hold",
        "sinc_best",
        "sinc_fastest",
        "sinc_medium",
    ):
        # Use numpy to vectorize the resampler along the target axis
        # This is because samplerate does not support ndim>2 generally.
        y_hat = np.apply_along_axis(
            samplerate.resample, axis=axis, arr=y, ratio=ratio, converter_type=res_type
        )
    elif res_type.startswith("soxr"):
        # Use numpy to vectorize the resampler along the target axis
        # This is because soxr does not support ndim>2 generally.
        y_hat = np.apply_along_axis(
            soxr.resample,
            axis=axis,
            arr=y,
            in_rate=orig_sr,
            out_rate=target_sr,
            quality=res_type,
        )
    else:
        y_hat = resampy.resample(y, orig_sr, target_sr, filter=res_type, axis=axis)

    if fix:
        y_hat = util.fix_length(y_hat, size=n_samples, axis=axis, **kwargs)

    if scale:
        y_hat /= np.sqrt(ratio)

    # Match dtypes
    return np.asarray(y_hat, dtype=y.dtype)
