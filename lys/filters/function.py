# all filter classes
_filterClasses = {}
_filterGuis = {}
# all filter GUIs
_filterGroups = {}


def addFilter(filter, filterName=None, gui=None, guiName=None, guiGroup=None):
    """
    Add new filter to lys.

    Args:
        filter(class that implements FilterInterface): filter to be added.
        filterName(str): name of filter. If omitted, default name is used.
        gui(class that implements FilterSettingBase, and is decorated by filterGUI): Widget that is used in FilterGUI.
        guiName(str): name of filter in GUI.
        guiGroup(str): name of group in GUI.
    """
    # set default name
    if filterName is None:
        filterName = filter.__name__
    if guiName is None:
        guiName = filterName
    # register filter
    _filterClasses[filterName] = filter
    # register gui
    if gui is not None:
        _filterGuis[filterName] = gui
        if guiGroup is None:
            _filterGroups[guiName] = gui
        elif guiGroup in _filterGroups:
            _filterGroups[guiGroup][guiName] = gui
        else:
            _filterGroups[guiGroup] = {guiName: gui}


def getFilter(filterName):
    """
    Get a filter class from name.

    Args:
        name(str): The name of the filter. See :func:`addFilter`.

    Returns:
        filterClass: The filter class
    """
    if filterName in _filterClasses:
        return _filterClasses[filterName]
    else:
        return None


def _getFilterName(filter):
    for key, item in _filterClasses.items():
        if item == type(filter) or item == filter:
            return key


def _getFilterGui(filter):
    return _filterGuis[_getFilterName(filter)]


def _getFilterGuiName(filter):
    for key, item in _filterGroups.items():
        if key == "":
            continue
        if isinstance(item, dict):
            for key2, item2 in item.items():
                if item2.getFilterClass() == filter or item2.getFilterClass() == type(filter):
                    return key2
        else:
            if item.getFilterClass() == filter or item.getFilterClass() == type(filter):
                return key


def fromFile(file):
    """
    Load filter from .fil file.

    Args: 
        file(str): The path to the .fil file

    Returns:
        filter: The filter loaded form the .fil file. 

    Example::

        from lys import filters
        # Create filter
        f = filters.IntegralAllFilter(axes=[0], sumtype="Sum")

        # Save filter as file
        filter_string = filters.toFile(f, "test.fil") 

        # Load filter from file
        filt = filters.fromFile("test.fil")

        # Execute
        filt.execute(np.ones([3,3]))
        # [3. 3. 3.]
    """
    from lys.filters import Filters
    return Filters.fromFile(file)


def toFile(filter, file):
    """
    Save filter to .fil file.

    Args:
        filter: The filter to be saved.
        file: The filepath.

    """
    filter.saveAsFile(file)


def fromString(string):
    """
    Load filter from string that is generated by :func:`toString` function.

    Args: 
        string(str): The string that is generated by :func:`toString` function.

    Returns:
        filter: The filter loaded form the string. 

    Example::

        from lys import filters
        # Create filter
        f = filters.IntegralAllFilter(axes=[0], sumtype="Sum")

        # Save filter as string
        filter_string = filters.toString(f) 

        # Load filter from string
        filt = filters.fromString(filter_string)

        # Execute
        filt.execute(np.ones([3,3]))
        # [3. 3. 3.]
    """
    from lys.filters import Filters
    return Filters.fromString(string)


def toString(filter):
    """
    Save filter as file. The filter can be loaded by :func:`fromString` function.

    Args:
        filter: The filter instance.

    Returns:
        str: The string containing the information of the filter.


    """
    from lys.filters import Filters
    return Filters.toString(filter)
