# Data Description
The code we have provided uses the first-minute IP trace downloaded from CAIDA 2019. Due to the spread measurement task, all algorithms can drop the duplicate stream items. Therefore, we consider the transmission size of GitHub (<25MB) and upload the de-duplicated datasets `00_four.7z` and `00_six.7z`. If you wish to verify the complete dataset of all traffic, please visit the url https://www.caida.org/catalog/datasets/passive_dataset/.

`00_four.7z`: The dataset used in the four-task spread measurement, each stream item is modeled as: (src, dst, sport, dport).

`00_six.7z`: The dataset used in the six-task spread measurement, each stream item is modeled as: (src, dst, sport, dport, prot).

`00_four.txt`: A simple demo used to ensure the proper functioning of the algorithm in **four-task spread measurement**, containing only one PSD flow from the IP address 79.127.180.42, with an actual PSD spread of 94621. Therefore, to test with real one-minute traffic data, the demo file should be deleted, and the dataset file should be renamed to `00_four.txt`.

`00_six.txt`: A simple demo used to ensure the proper functioning of the algorithm in **six-task spread measurement**, containing only one PSD flow from the IP address 79.127.180.42, with an actual PSD spread of 94621. Therefore, to test with real one-minute traffic data, the demo file should be deleted, and the dataset file should be renamed to `00_six.txt`.
