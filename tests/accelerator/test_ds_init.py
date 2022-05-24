import os
import torch
import deepspeed
import deepspeed.accelerator as accel


class OneLayerNet(torch.nn.Module):
    def __init__(self, D_in, D_out):
        """
        In the constructor we instantiate two nn.Linear modules and assign them as
        member variables.
        """
        super(OneLayerNet, self).__init__()
        self.linear1 = torch.nn.Linear(D_in, D_out)

    def forward(self, x):
        """
        In the forward function we accept a Variable of input data and we must return
        a Variable of output data. We can use Modules defined in the constructor as
        well as arbitrary operators on Variables.
        """
        h_relu = self.linear1(x).clamp(min=0)
        y_pred = self.linear1(h_relu)
        return y_pred


def test_literal_device():
    model = OneLayerNet(128, 128)

    os.environ['RANK'] = '0'
    os.environ['WORLD_SIZE'] = '1'
    os.environ['MASTER_ADDR'] = '127.0.0.1'
    os.environ['MASTER_PORT'] = '8088'
    os.environ['LOCAL_RANK'] = '0'
    if accel.literal_device() == 'cuda':
        deepspeed.init_distributed('nccl')
    else:
        deepspeed.init_distributed('ccl')
    deepspeed.initialize(model=model, config='ds_config.json')
    string = accel.literal_device()  #'xpu' or 'cuda'
    string0 = accel.literal_device(0)  #'xpu:0' or 'cuda:0'
    string1 = accel.literal_device(1)  #'xpu:1' or 'cuda:1'
    assert string == 'xpu' or string == 'cuda'
    assert string0 == 'xpu:0' or string0 == 'cuda:0'
    assert string1 == 'xpu:1' or string1 == 'cuda:1'
