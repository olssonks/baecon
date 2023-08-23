.. _contribution_guide:

Contributions Guide
+++++++++++++++++++

Welcome to the contritutions guide. To begin, create a working environment 
following the instructions below.


Setup ``baecon`` Development Environment
========================================

Starting from scratch, install the ``Python`` package and environment manager ``conda`` (or  ``mamba``).

``baecon`` uses packages from both ``conda`` and ``pip``. It is easiest to combine these
is with a conda environment. To install ``conda`` follow the instructions here: 
`miniconda <https://docs.conda.io/en/latest/miniconda.html>`_. 

**Recommended**: alternitavely 
you can use ``mamba``, a drop in replacement for `conda`, which is much faster for installing 
packages. Installation instructions here: `mamba <https://mamba.readthedocs.io/en/latest/mamba-installation.html#mamba-install>`_. 
**Warning**: Only use ``mamba`` is you have no existing ``conda`` installation. Otherwise, 
uninstall ``conda`` first.

Now move to your favorite working directiory grab the repo at `<https://github.com/olssonks/baecon.git>`_
with the following commands:

.. code-block:: bash
    
    git clone https://github.com/olssonks/baecon.git baecon
    cd baecon 

This should look similar to this 

.. code-block:: bash

    (base) walsworth1:.../users/walsworth1/documents$ git clone https://github.com/olssonks/baecon.git baecon
    Cloning into 'baecon'...
    remote: Enumerating objects: 1877, done.
    remote: Counting objects: 100% (215/215), done.
    remote: Compressing objects: 100% (145/145), done.
    remote: Total 1877 (delta 94), reused 138 (delta 55), pack-reused 1662
    Receiving objects: 100% (1877/1877), 16.49 MiB | 19.89 MiB/s, done.
    Resolving deltas: 100% (1009/1009), done.
    Updating files: 100% (262/262), done.
    (base) walsworth1:.../users/walsworth1/documents$ cd baecon
    (base) walsworth1:.../walsworth1/documents/baecon$ ls
    LICENSE     development_info  docs         pyproject.toml   requirements-docs.txt  src    tools
    README.rst  dist              exp_configs  readthedocs.yml  requirements.txt       tests
    (base) walsworth1:.../walsworth1/documents/baecon$


Move to the ``development\baecon_environment`` directiory and 
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

Finally, move back to the main ``baecon``directionary and  install ``baecon`` 
as an editable package:

.. code-block:: bash

    cd ../..
    pip install --editable .
    
During the installation, it may pause on the following line

.. code-block:: bash
    
    Successfully built baecon
    Installing collected packages: ...

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

