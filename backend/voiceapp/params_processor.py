import numpy as np
from scipy.signal import savgol_filter


def process_params(params, length):
    params_array = np.array(params)
    transposed_array = np.transpose(params_array, (1, 0, 2))
    reshaped_array = transposed_array.reshape(8, 94 * length)

    filtered_params = []
    for i in range(len(reshaped_array)):
        filtered_params.append(savgol_filter(reshaped_array[i], window_length=32, polyorder=2).tolist())

    return filtered_params
