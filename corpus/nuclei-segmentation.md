# Segmenting and counting nuclei in fluorescence microscopy

## Why it matters

Counting nuclei stained with DAPI or Hoechst is the first step of many cell-based assays: proliferation, toxicity screens and the mitotic index. Per-nucleus intensity integrated over the area is proportional to DNA content and separates G1, S and G2/M cells.

## Classical pipeline

1. Smooth the image and subtract an uneven background.
2. Threshold, for example with Otsu's method.
3. Split touching nuclei with a marker-controlled watershed: compute the distance transform of the foreground mask, take its local maxima as one marker per nucleus, and flood the inverted distance map from the markers. Basins meet along the narrow neck between two touching nuclei.

Without the watershed, touching nuclei are counted as one object, so counts are too low in dense regions.

## Deep learning

StarDist (Schmidt et al. 2018) predicts star-convex polygons and works well for round nuclei. Cellpose (Stringer et al. 2021) predicts flow fields towards cell centres and generalises to many cell types. Both need far less tuning than classical pipelines on difficult images.

## Evaluation

Instance segmentation is evaluated by matching predicted and true objects: a prediction counts as correct if its intersection over union (IoU) with a true object is at least a threshold such as 0.5. Precision, recall and F1 follow from the matches. The 2018 Data Science Bowl averaged this over IoU thresholds from 0.5 to 0.95.
