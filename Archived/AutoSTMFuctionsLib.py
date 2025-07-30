import numpy as np 
import matplotlib.pyplot as plt
import os
import io
import inspect


def load_txt_from_idl(path, filename, global_namespace=None):
    """To load txt file in given path and convert it into numpy array

    Args:
        path (string): The path to load the txt file.
        filename (string): The name of the txt file.
    """
    # Load the text file into a numpy matrix
    matrix = np.loadtxt(os.path.join(path, filename))
    var_name = 'x' + filename[0:-4]

    len_matrix = len(matrix)
    new_matrix = np.zeros((len_matrix,len_matrix))

    for i in range(len_matrix):
        new_matrix[len_matrix-1-i,:] = matrix[i,:]
    
    global_namespace[var_name] = new_matrix
    global_namespace['image_pool'].append(var_name)


def plot_topo(topo,global_namespace=None):
    """To plot 2d numpy array as topography image 

    Args:
        topo (str): The 2d array that need to be ploted.
    """
    topo_array=global_namespace[topo]
    # Display the matrix as an image
    plt.imshow(topo_array, cmap = 'Blues_r', interpolation = 'none')
    plt.colorbar()
    plt.title(topo)
    plt.axis('off')
    plt.show()

def plot_fft(data_name,hist,global_namespace=None):
    """To plot 2d numpy array as Fourier Transform image

    Args:
        data_name (str): The 2d array that need to be ploted.
        hist (list): The histogram range to show.
    """
    data = global_namespace[data_name]
    if not hist:
        plt.imshow(np.log(data+1), cmap='gray_r')
    else:
        plt.imshow(data, cmap='gray_r',vmin = int(hist[0]),vmax = int(hist[1]))
    plt.title(data_name+'_FFT_Amp')
    plt.colorbar()
    plt.axis('off')
    plt.show()


def polybackRow(data_name, polyord, global_namespace=None):
    """To subtract the background from an image using polynomial fitting. 

    Args:
        data_name (str): Variable name of the image to subtract background.
        polyord (str): The order of polynomial fitting. It should be an integer number in string type. eg: '2'
    """
    curr_data = global_namespace[data_name]
    
    xsize, ysize = curr_data.shape

    new_data = np.zeros((xsize, ysize))

    x = np.arange(1, xsize+1)

    for i in range(ysize):
        y = curr_data[:, i]
        pFit = np.polyfit(x, y, int(polyord))
        pFity = np.polyval(pFit, x)
        new_data[:, i] = y - pFity
    global_namespace[data_name+'_polyback_'+polyord] = new_data
    if 'image_pool'+'_polyback_'+polyord in global_namespace:
        global_namespace['image_pool'+'_polyback_'+polyord].append(data_name+'_polyback_'+polyord)
    else:
        global_namespace['image_pool'+'_polyback_'+polyord]=[]
        global_namespace['image_pool'+'_polyback_'+polyord].append(data_name+'_polyback_'+polyord)
    
def fftamp(data, global_namespace=None):
    """Perform Fuorier Transform on provided image, and return the amplitude.

    Args:
        data (str): Variable name of the image to perform Fourier transform.
    """
    var_name = data+'_FFT_Amp'
    image_data = global_namespace[data]
    fourier_transform_shifted = np.abs(np.fft.fftshift(np.fft.fft2(image_data)))
    global_namespace[var_name] = fourier_transform_shifted
    if 'image_pool'+'_FFT_Amp' in global_namespace:
        global_namespace['image_pool'+'_FFT_Amp'].append(var_name)
    else:
        global_namespace['image_pool'+'_FFT_Amp']=[]
        global_namespace['image_pool'+'_FFT_Amp'].append(var_name)



def npay2str(data_array, global_namespace=None):
    """To convert nd numpy array into a string so that chat model could read. 

    Args:
        data_array (array): The nd array that needs to be converted.
    """
    if isinstance(data_array,np.ndarray):
        string_io = io.StringIO()
        np.savetxt(string_io,data_array, delimiter=' ')
        data_string = string_io.getvalue()
        return data_string
    else:
        print("Error, input argument is not a numpy array")

def str2npay(data_string, global_namespace=None):
    """To convert string into numpy array

    Args:
        data_string (str): The string needed to convert.
    """
    if isinstance(data_string,str):
        string_io = io.StringIO(data_string)
        data_array = np.loadtxt(string_io, delimiter=' ')
        return data_array
    else:
        print("Error, input argument is not a string array")
        
def get_variable_name(var, namespace):
    return [name for name in namespace if namespace[name] is var]
