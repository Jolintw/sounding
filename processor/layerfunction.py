import numpy as np

class Layer:
    def __init__(self, layer = None):
        self.bottom_ind = np.array([])
        self.top_ind = np.array([])
        self.count_layer()
        if layer:
            self.copy

    def find_layers_from_1Dmask(self, mask):
        self.mask = mask
        mask_int = mask.astype(int)
        mask_int = np.append([0], mask_int) # pad a dry layer to the ground
        mask_int = np.append(mask_int, [0]) # pad a dry layer to the end of sounding
        diff = mask_int[1:] - mask_int[:-1] 
        # 1 in diff means next element is first element of Trues in mask_int
        # -1 means the last element in Trues
        # but index n of diff corresponding to n+1 of sounding
        full_ind = np.arange(len(diff), dtype=int)
        self.bottom_ind = full_ind[diff==1]
        self.top_ind    = (full_ind - 1)[diff==-1]
        
        return self.count_layer()
    
    def count_layer(self):
        self.layer_number = len(self.bottom_ind)
        return self.layer_number
    
    def get_bottom_top_value(self, var, postfix):
        setattr(self, "bottom_"+postfix, var[self.bottom_ind])
        setattr(self, "top_"+postfix, var[self.top_ind])
        return getattr(self, "bottom_"+postfix), getattr(self, "top_"+postfix)
    
    def get_max_value_in_layer(self, var, prefix):
        maxvalue = []
        for bi, ti in zip(self.bottom_ind, self.top_ind):
            maxvalue.append(np.nanmax(var[bi:ti+1]))
        setattr(self, prefix+"_max", np.array(maxvalue))
        return getattr(self, prefix+"_max")
    
    def get_max_ind_in_layer(self, var, prefix):
        maxind = []
        for bi, ti in zip(self.bottom_ind, self.top_ind):
            maxind.append(np.nanargmax(var[bi:ti+1]) + bi)
        setattr(self, prefix+"_maxind", np.array(maxind))
        return getattr(self, prefix+"_maxind")

    def get_mask_of_layer(self, var):
        """
        return a boolean array has length of var
        True for layer exist at that ind
        """
        mask = np.zeros_like(var, dtype=bool)
        for cloud in range(self.layer_number):
            bi = self.bottom_ind[cloud]
            ti = self.top_ind[cloud]
            mask[bi:ti+1] = True
        self.mask = mask
        return mask
    
    def get_keys_of_variables(self):
        """
        return the names of variables of every layer
        """
        keys = list(self.__dict__)
        newkeys = []
        for key in keys:
            value = getattr(self, key)
            if isinstance(value, np.ndarray):
                if len(value) == self.layer_number:
                    newkeys.append(key)
        return newkeys
    
    def mask_out_layers(self, mask):
        """
        param mask: length of mask == layer_number
        layers with False in coressponding index in mask will be removed
        """
        keys = self.get_keys_of_variables()
        for key in keys:
            value = getattr(self, key)[mask]
            setattr(self, key, value)
        self.count_layer()

    def copy(self):
        newlayer = Layer()
        keys = self.get_keys_of_variables()
        for key in keys:
            value = getattr(self, key).copy()
            setattr(newlayer, key, value)
        newlayer.count_layer()
        return newlayer