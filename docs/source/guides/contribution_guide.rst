.. _contribution_guide:

Contributions Guide
+++++++++++++++++++

Welcome to the contritutions guide. To begin, create a working environment 
following the instructions below.


Setup ``baecon`` Development Environment
========================================

If you haven't installed ``baecon``, first follow the installation instructions
here: :ref:`readme_link`.

``baecon`` uses packages from both ``conda`` and ``pip``. It is easiest to combine these
is with a conda environment. To install ``conda`` follow the instructions here: 
`miniconda <https://docs.conda.io/en/latest/miniconda.html>`_. 

**Recommended**: alternitavely 
you can use ``mamba``, a drop in replacement for `conda`, which is much faster for installing 
packages. Installation instructions here: `mamba <https://mamba.readthedocs.io/en/latest/mamba-installation.html#mamba-install>`. 
**Warning**: Only use ``mamba`` is you have no existing ``conda`` installation. Otherwise, 
uninstall ``conda`` first.

With ``conda`` installed (or ``mamba``), move to the ``development\baecon_environment`` directiory and 
use the following command to create the conda portion ``baecon`` environment

.. code-block:: bash

    conda create env -n baecon --file baecon_conda_env.yml
    
Next, activate the newly created conda environment ``baecon``:

.. code-block:: bash

    conda activate baecon
    
Then, install the `pip` requirements:

.. code-block:: bash 

    pip install -r baecon_pip_requirements.txt
    
**Important: You must create and activate the conda environment first, or there will
be issues with using the pip requirements.**

Finally install ``baecon`` as an editable package:

.. code-block:: bash

    pip install --editable .

The environment files ``baecon_conda_env.yml`` and ``baecon_pip_requirements.txt`` only list
the explicitly need Python packages. ``conda`` and ``pip`` will install the other necessary 
packages. This allows for cross-platform combatibility, as some packages needed for the 
explicitly list packages are platform specific.

You are now ready to work on ``baecon``. Remember to activate your ``baecon`` environment 
when working on this project.

.. todo:: 
    Create test to check environment is correctly installed.
    

Creating a Development Branch
=============================

First, create an issue to describe the job you will be working on, such as adding
a new device or fixing a bug. Then create a new branch, using ``dev`` as the source
for the new branch. The name of the branch should be ``dev_issue-##_<yourname>``.

Contributions are made through merging new branches into ``dev``. To begin working on a job 
(new feature, bug fix, etc.), create an issue and a branch with the name 
``dev_issue-##_<yourname>``. Make sure the ``dev`` is the source for the new branch
you create. 

Step by Step:
-------------
    #. On the GitHub web interface, create a new issue describing what you will be working on.
    #. From the issue, click on the  "Create a branch" link on the 
       right of the issue page, under "Development".
    #. On the "Create a branch for this issue" window, enter a name for the branch 
       ``dev_issue-##_<yourname>``.
    #. Click on "Change branch source" underneath the name entry, and make sure the
       source is the ``dev`` branch.
    #. The select "Checkout locally" and create the branch.
    #. On your local repo use the commands ``git fetch origin`` and the 
       ``git pull origin <new branch>``.


Making Commits
==============
Version control and change logs are managed with a `commitizen <https://commitizen-tools.github.io/commitizen/>`_.
The change necessary to the typeical work flow is that instead of ``git commit`` you use ``git-cz commit``. 
All other ``git`` commands stay the same. When making a commit this way, a menu in the commandline 
will walk you through the proper way to make commits.

Version control and change logs follow the `Conventional Commits <https://www.conventionalcommits.org/en/v1.0.0/>`_.

