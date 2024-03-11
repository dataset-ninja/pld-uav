**PLD-UAV: Power Line Detection in UAV** is a dataset for instance segmentation, semantic segmentation, and object detection tasks. It is used in the energy industry, and in the drone inspection domain. 

The dataset consists of 11210 images with 240553 labeled objects belonging to 1 single class (*power_line*).

Images in the PLD-UAV dataset have pixel-level instance segmentation annotations. Due to the nature of the instance segmentation task, it can be automatically transformed into a semantic segmentation (only one mask for every class) or object detection (bounding boxes for every object) tasks. There are 8 (0% of the total) unlabeled images (i.e. without annotations). There are 4 splits in the dataset: *PLDU-train* (7248 images), *PLDM-train* (3792 images), *PLDU-test* (120 images), and *PLDM-test* (50 images). Additionally, ***aug*** tag characterizes the degree of an augmentation. Also, every image is grouped by its ***image_id***. Explore them in supervisely labeling tool. The dataset was released in 2019 by the <span style="font-weight: 600; color: grey; border-bottom: 1px dashed #d3d3d3;">Wuhan University, China</span> and <span style="font-weight: 600; color: grey; border-bottom: 1px dashed #d3d3d3;">LIESMARS, China</span>.

<img src="https://github.com/dataset-ninja/pld-uav/raw/main/visualizations/poster.png">
