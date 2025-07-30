from executioner import call_matlab_meta

def opensxm_auto(path, fn, pnum=1):
    """
    Wrapper for MATLAB script 'opensxm'.

    This function directly calls the MATLAB script `opensxm` to load SXM files.
    No figure activation is required because it creates a new figure internally.

    Parameters:
        pnum (int): Load mode (1=single forward topo, 2=all images, 3=forward only).

    Returns:
        Result variable name or status (handled by MATLAB side).
    """
    return call_matlab_meta({
        "script": "opensxm_auto",
        "params": [{"path": path},{"filename": fn},{"pnum": pnum}],
        "outputs": ["sxm_data"]
    })



def image_polybackrow(figure_name, pnum=2):
    """
    Wrapper for MATLAB script 'image_polybackrow'.

    This function activates the target figure and applies polynomial background
    subtraction row-wise using the original MATLAB script `image_polybackrow`.

    Parameters:
        figure_name (str): The variable name of the figure handle in MATLAB workspace.
        pnum (int): Polynomial degree for background subtraction.

    Returns:
        Result variable name or status (handled by MATLAB side).
    """
    # Step 1: Activate target figure
    call_matlab_meta({
        "script": "activate_tgt_fig_for_gcf",
        "params": {"figure_handle_var": figure_name},
        "outputs": []
    })

    # Step 2: Execute the original MATLAB script
    return call_matlab_meta({
        "script": "image_polybackrow",
        "params": {"pnum": pnum},
        "outputs": ["polyback_result"]
    })


def image_Fourier_Transform(figure_name, pnum=3):
    """
    Wrapper for MATLAB script 'image_Fourier_Transform'.

    This function first activates the target figure in MATLAB workspace
    using its handle variable name, then calls the original MATLAB script
    `image_Fourier_Transform` with the specified parameter.

    Parameters:
        figure_name (str): The variable name of the figure handle in MATLAB workspace.
        pnum (int): Mode of Fourier transform (1=real, 2=imag, 3=amplitude, 4=phase).

    Returns:
        Result variable name or status (handled by MATLAB side).
    """
    # Step 1: Activate target figure
    call_matlab_meta({
        "script": "activate_tgt_fig_for_gcf",
        "params": {"figure_handle_var": figure_name},
        "outputs": []
    })

    # Step 2: Execute the original MATLAB script
    return call_matlab_meta({
        "script": "image_Fourier_Transform",
        "params": {"pnum": pnum},
        "outputs": ["fft_result"]
    })


def image_Extract_Linecut(figure_name):
    """
    Wrapper for MATLAB script 'image_Extract_Linecut'.

    This function activates the target figure and then calls the MATLAB script
    `image_Extract_Linecut` to extract and plot linecuts interactively.

    Parameters:
        figure_name (str): The variable name of the figure handle in MATLAB workspace.

    Returns:
        Result variable name or status (handled by MATLAB side).
    """
    # Step 1: Activate target figure
    call_matlab_meta({
        "script": "activate_tgt_fig_for_gcf",
        "params": {"figure_handle_var": figure_name},
        "outputs": []
    })

    # Step 2: Execute the original MATLAB script
    return call_matlab_meta({
        "script": "image_Extract_Linecut",
        "params": {},
        "outputs": ["linecut_result"]
    })

