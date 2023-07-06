GUI
===

The :py:mod:`baecon` GUI is a web app made using the the `NiceGUI <https://nicegui.io/>`_ 
package. The GUI runs in a browser with :py:mod:`baecon` running in the background. 
The GUI allows for configuration of the various :py:mod:`baecon` objects and choosing
file paths to from which to save and load. All devices appear in the GUI under
a devices tab, though device specific GUIs can be made and called from the device
tab/window.

The GUI consists of a main window defined by :py:mod:`baecon.GUI.baecon_GUI.main`.
The module organizes the submodules corresponding to the other :py:mod:`baecon`
objects, which are represented as :py:mod:`nicegui.ui.card` objects. In addition
there is the :py:mod:`baecon.GUI.gui_utils` which has methods and dataclasses
used in all the GUI components, like file loading or value holding.

.. toctree::
   :maxdepth: 1
   :caption: Contents:
   
   GUI_components/main_gui
   GUI_components/data_card
   GUI_components/devices_card
   GUI_components/engine_card
   GUI_components/experiment_card
   GUI_components/plot_card
   GUI_components/scan_card

Example image 

.. image:: ./_static/GUI_image.png