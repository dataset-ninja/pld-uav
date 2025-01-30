Dataset **PLD-UAV** can be downloaded in [Supervisely format](https://developer.supervisely.com/api-references/supervisely-annotation-json-format):

 [Download](https://assets.supervisely.com/remote/eyJsaW5rIjogImZzOi8vYXNzZXRzLzIyNjhfUExELVVBVi9wbGR1YXYtRGF0YXNldE5pbmphLnRhciIsICJzaWciOiAiVnYwUnpHN2dqekw1MGl0T1RRc08vVTlrdmJRdVl4dVQ4a2FRVTdjb25oWT0ifQ==)

As an alternative, it can be downloaded with *dataset-tools* package:
``` bash
pip install --upgrade dataset-tools
```

... using following python code:
``` python
import dataset_tools as dtools

dtools.download(dataset='PLD-UAV', dst_dir='~/dataset-ninja/')
```
Make sure not to overlook the [python code example](https://developer.supervisely.com/getting-started/python-sdk-tutorials/iterate-over-a-local-project) available on the Supervisely Developer Portal. It will give you a clear idea of how to effortlessly work with the downloaded dataset.

The data in original format can be downloaded here:

- [PLDU](https://drive.google.com/open?id=1XjoWvHm2I8Y4RV_i9gEd93ZP-KryjJlm)
- [PLDM](https://drive.google.com/open?id=1bKFEuXKHRsy0tnOnoEVW6oRi7hS5oekr)
