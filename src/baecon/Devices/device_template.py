from baecon import Instrument


class New_Instrument(Instrument):
    def __init__(self, configuration: dict = None) -> None:
        """Add initionalization specifcs for the type of insturment.

        Args:
            configuration (dict, optional): _description_. Defaults to None.
        """        
        super.__init__(configuration)
        
        return


    # Writing and Reading will be device specfic as connect types and command are all different
    def write(self, parameter, value):
        """Add functionally to change the `parameter` to `value` on the 
            instrument.

        Args:
            parameter (_type_): _description_
            value (_type_): _description_
        """
        return

    def read(self, parameter, value):
        """Add functionally to read the value of `parameter` from the instrument.

        Args:
            parameter (_type_): _description_
            value (_type_): _description_
        """
        return

    def close_instrument(self) -> None:
        
        return


# end Instrument class
