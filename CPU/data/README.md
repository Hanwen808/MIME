# Data Description
The code we have provided uses the first-minute IP trace downloaded from CAIDA 2019. Due to the spread measurement task, all algorithms can drop the duplicate stream items. Therefore, we consider the transmission size of GitHub (<25MB) and upload the de-duplicated dataset `00_three_task.7z`. If you wish to verify the complete dataset of all traffic, please visit the url https://www.caida.org/catalog/datasets/passive_dataset/.

This data is used to test the off-chip update throughput of all algorithms, where each line is `src dst dport`.

The data file `00.txt` is a simple demo used to ensure the proper functioning of the algorithm, containing only one PSD flow 79.127.180.42, with an actual PSD spread of 94621. 
Therefore, to test with real one-minute traffic data, the demo file `00.txt` should be deleted, and the dataset file should be renamed to `00.txt`.

Before running the throughput experiment, you first need to decompress the 00_three_task.7z file and move 00.txt from the decompressed directory ./00_three_task/ to the current directory. The specific commands are as follows
```bash
$ sudo apt install p7zip-full
$ 7z x 00_three_task.7z
$ mv ./00_three_task/00.txt ./
```
