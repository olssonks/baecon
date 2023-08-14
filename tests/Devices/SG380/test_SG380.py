import pathlib

import baecon as bc
import pytest
from baecon.Devices import SG380

default_file = pathlib.Path(SG380.__file__).parent / "default.toml"

default_config = bc.utils.load_config(default_file)


def test_init():
    ## make SG380

    assert default_config['parametergs'] == sg380

    return
