# Python Source Code for MIME

## Descriptions

- `./MIME_four.py`: source codes for four-task spread estimation.
- `./MIME_six.py`: source codes for six-task spread estimation.
- `./superhost_detect.py`: source codes for superhost detection.
- `./super_kpse.py`: source codes for super k-persistent spread estimation. Since the sKPSE task requires collecting multiple supercubes using MIME over several periods, we only provide the code for executing sKPSE based on the collected supercubes.

## Run

To run the codes with your computer, you should first install the following python modules.
```shell
$ pip install mmh3
$ pip install matplotlib
$ pip install numpy
$ pip install pandas
$ pip install tqdm
```
or
```shell
$ pip3 install mmh3
$ pip3 install matplotlib
$ pip3 install numpy
$ pip3 install pandas
$ pip3 install tqdm
```
Then please unzip the relevant dataset files under `./datas/`, the dataset descriptions are provided in `./datas/README.md`.

The Python execution commands for different tasks are copied as below

(1) four-task spread measurement:
```shell
$ python ./MIME_four.py
```
or
```shell
$ python3 ./MIME_four.py
```

(2) six-task spread measurement:
```shell
$ python ./MIME_six.py
```
or
```shell
$ python3 ./MIME_six.py
```

(3) superhost detection:
```shell
$ python ./superhost_detect.py
```
or
```shell
$ python3 ./superhost_detect.py
```

(4) super k-persistent spread measurement:
```shell
$ python ./super_kpse.py
```
or
```shell
$ python3 ./super_kpse.py
```

Note that, the dataset, memory configuration, the number of different flow items, and the supported tasks need to be modified in the main function of the Python file.
For example, if you want to evaluate performance in different memories (300KB, 500KB, 700KB, 900KB), the paramter $m$ should be reset as below
```shell
N = 2607408  # 11405665. 2607408 is the number of distinct stream items in one minute trace, 11405665 is the number of distinct stream items in five minute trace
for m in [300, 500, 700, 900]:
    p, k = search_for_k_p(N, m * 8 * 1024)  # get_opt_sampling_rates(N, m * 8 * 1024)
```
