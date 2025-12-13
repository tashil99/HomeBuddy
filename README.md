# Home Buddy 🤖

Home Buddy is a smart autonomous robot project that integrates **computer vision, object detection, and robot control**. This repository contains the full pipeline used during development and demonstration, including data preprocessing, model training/testing, and the final deployment script used on the robot.

---

## Repository Structure

```
.
├── home-buddy.py          # Main script used on the robot (demo/runtime)
├── scripts/               # Supporting scripts (data preprocessing, training, testing)
├── merged-dataset/        # Prepared/merged datasets for training
├── .idea/                 # IDE configuration files
└── README.md              # Project documentation
```

---

## Main Script 

### `home-buddy.py`

This is the **core script used during the robot demonstration**. It is responsible for:

* Running real-time object detection
* Interaction with the robot hardware (motors, sensors)
* Making movement and control decisions based on detected objects
* Integrating the trained detection model into the live system

---

##  Supporting Scripts

The `scripts/` directory contains additional code used during development, including:

* **Data preprocessing** (cleaning, merging, formatting datasets)
* **Model training** for object detection
* **Model evaluation and testing**
* Experimental or testing scripts not used directly in the live demo

These scripts are not required for running the robot demo but were essential for **training the YOLO model**.

---

## Dataset

The `merged-dataset/` folder contains the processed dataset used for training the object detection model. This dataset is the result of combining and preparing raw data to be compatible with the training pipeline.

---

## Technologies Used

* **Python3**
* **YOLO (Ultralytics)** for object detection
* **OpenCV** for image processing
* **Robot control libraries** (Rosmaster_Lib)
* **Serial communication** for hardware interfacing

---

## Usage

To run the robot using the trained model:

```bash
python3 home-buddy.py
```

> Note: This script is intended to run on raspberry pi

---

## Notes

* `home-buddy.py` was the **exact script used during the demo**.
* Other scripts are included for **transparency, reproducibility, and further development**.
* Paths to models and datasets may need adjustment depending on your system setup.

---
