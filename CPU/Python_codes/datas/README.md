# Data Description
The code we have provided uses the first-minute IP trace downloaded from CAIDA 2019. Due to the spread measurement task, all algorithms can drop the duplicate stream items. Therefore, we consider the transmission size of GitHub (<25MB) and will upload the de-duplicated dataset. If you wish to verify the complete dataset of all traffic, please visit the url https://www.caida.org/catalog/datasets/passive_dataset/.

`00_processed.7z`: The dataset used in the four-task spread measurement, each stream item is modeled as: (src, dst, sport, dport).

`00_prot_unique.7z`: The dataset used in the six-task spread measurement, each stream item is modeled as: (src, dst, sport, dport, prot).
