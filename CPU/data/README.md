# Data Description
The code we have provided uses the first-minute IP trace downloaded from CAIDA 2019. Due to the spread measurement task, all algorithms can drop the duplicate stream items. Therefore, we consider the transmission size of GitHub (<25MB) and will upload the de-duplicated dataset. If you wish to verify the complete dataset of all traffic, please visit the url https://www.caida.org/catalog/datasets/passive_dataset/.

This data is used to test the off-chip update throughput of all algorithms, where each line is `src dst dport`.

Before running the throughput experiment, you first need to decompress the 00_three_task.7z file and move 00.txt from the decompressed directory ./00_three_task/ to the current directory. The specific commands are as follows
```bash
$ sudo apt install p7zip-full
$ 7z x 00_three_task.7z
$ mv ./00_three_task/00.txt ./
```
