from executioner import call_matlab_meta

def opensxm_auto(path, fn, pnum="1"):
    """
    Wrapper for the MATLAB script `opensxm_auto`.

    This wrapper loads an SXM file from a specified directory and file name,
    and delegates the actual file handling to MATLAB. Unlike figure-based
    operations, this function initializes its own figure internally, so no
    prior figure activation is required.

    Parameters:
        path (str): Directory path containing the SXM file.
        fn (str): Name of the SXM file to be loaded (including extension).
        pnum (str, optional): Load mode selector:
            1 = Load single forward topography (default)
            2 = Load all available images
            3 = Load forward-only images

    Returns:
        dict: A dictionary containing variable(s) created or updated
        within the MATLAB workspace, as identified by the namespace manager.
    """
    return call_matlab_meta({
        "script": "opensxm_auto",
        "params": [{"path": path},{"filename": fn},{"pnum": pnum}],
        "outputs": ["sxm_data"]
    })



def image_polybackrow(figure_name, pnum="2"):
    """
    Wrapper for MATLAB script 'image_polybackrow'.

    This function activates the target figure and applies polynomial background
    subtraction row-wise using the original MATLAB script `image_polybackrow`.

    Parameters:
        figure_name (str): The variable name of the figure handle in MATLAB workspace.
        pnum (str): Polynomial degree for background subtraction. Should only be 1,2,3.

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


def image_Fourier_Transform(figure_name, pnum="3"):
    """
    Wrapper for MATLAB script 'image_Fourier_Transform'.

    This function first activates the target figure in MATLAB workspace
    using its handle variable name, then calls the original MATLAB script
    `image_Fourier_Transform` with the specified parameter.

    Parameters:
        figure_name (str): The variable name of the figure handle in MATLAB workspace.
        pnum (string): Mode of Fourier transform (1=real, 2=imag, 3=amplitude, 4=phase).

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

