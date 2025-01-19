# Data Description
The code we have provided uses the first-minute IP trace downloaded from CAIDA 2019. Due to the spread measurement task, all algorithms can drop the duplicate stream items. Therefore, we consider the transmission size of GitHub (<25MB) and upload the de-duplicated datasets `00_three.7z`, `00_four.7z`, and `00_six.7z`. If you wish to verify the complete dataset of all traffic, please visit the url https://www.caida.org/catalog/datasets/passive_dataset/.

(1)`00_three.7z`: The dataset used in the superhost detection, each stream item is modeled as (src dst dport).

(2)`00_four.7z`: The dataset used in the four-task spread measurement, each stream item is modeled as (src, dst, sport, dport).

(3)`00_six.7z`: The dataset used in the six-task spread measurement, each stream item is modeled as (src, dst, sport, dport, prot).

(4) `00_three.txt`: A simple demo used to ensure the proper functioning of `../superhost_detect.py`, containing only one PSD flow from the IP address 79.127.180.42, with an actual PSD spread of 94621. Therefore, to test with real one-minute traffic data, the demo file should be deleted, and the dataset file should be renamed to `00_three.txt`.

(5)`00_four.txt`: A simple demo used to ensure the proper functioning of `../MIME_four.py`, containing only one PSD flow from the IP address 79.127.180.42, with an actual PSD spread of 94621. Therefore, to test with real one-minute traffic data, the demo file should be deleted, and the dataset file should be renamed to `00_four.txt`.

(6)`00_six.txt`: A simple demo used to ensure the proper functioning of the algorithm in `../MIME_six.py`, containing only one PSD flow from the IP address 79.127.180.42, with an actual PSD spread of 94621. Therefore, to test with real one-minute traffic data, the demo file should be deleted, and the dataset file should be renamed to `00_six.txt`.
