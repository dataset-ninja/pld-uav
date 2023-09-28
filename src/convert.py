# https://github.com/SnorkerHeng/PLD-UAV

import glob
import os
import shutil
from urllib.parse import unquote, urlparse

import numpy as np
import supervisely as sly
from cv2 import connectedComponents
from dataset_tools.convert import unpack_if_archive
from dotenv import load_dotenv
from supervisely.io.fs import (
    dir_exists,
    file_exists,
    get_file_ext,
    get_file_name,
    get_file_name_with_ext,
    get_file_size,
)
from tqdm import tqdm

import src.settings as s


def download_dataset(teamfiles_dir: str) -> str:
    """Use it for large datasets to convert them on the instance"""
    api = sly.Api.from_env()
    team_id = sly.env.team_id()
    storage_dir = sly.app.get_data_dir()

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, str):
        parsed_url = urlparse(s.DOWNLOAD_ORIGINAL_URL)
        file_name_with_ext = os.path.basename(parsed_url.path)
        file_name_with_ext = unquote(file_name_with_ext)

        sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
        local_path = os.path.join(storage_dir, file_name_with_ext)
        teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

        fsize = api.file.get_directory_size(team_id, teamfiles_dir)
        with tqdm(
            desc=f"Downloading '{file_name_with_ext}' to buffer...",
            total=fsize,
            unit="B",
            unit_scale=True,
        ) as pbar:
            api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)
        dataset_path = unpack_if_archive(local_path)

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, dict):
        for file_name_with_ext, url in s.DOWNLOAD_ORIGINAL_URL.items():
            local_path = os.path.join(storage_dir, file_name_with_ext)
            teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

            if not os.path.exists(get_file_name(local_path)):
                fsize = api.file.get_directory_size(team_id, teamfiles_dir)
                with tqdm(
                    desc=f"Downloading '{file_name_with_ext}' to buffer...",
                    total=fsize,
                    unit="B",
                    unit_scale=True,
                ) as pbar:
                    api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)

                sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
                unpack_if_archive(local_path)
            else:
                sly.logger.info(
                    f"Archive '{file_name_with_ext}' was already unpacked to '{os.path.join(storage_dir, get_file_name(file_name_with_ext))}'. Skipping..."
                )

        dataset_path = storage_dir
    return dataset_path


def count_files(path, extension):
    count = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(extension):
                count += 1
    return count


def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:
    # project_name = "PLD-UAV"
    dataset_path = "/mnt/d/datasetninja-raw/pld-uav"
    batch_size = 30
    ds_name = "ds"
    images_ext = ".jpg"
    masks_ext = ".mat"
    images_folder_name = "test"
    masks_folder_name = "test_gt"

    images_ext = ".jpg"
    ann_ext = ".png"
    images_folder = "aug_data"
    masks_folder = "aug_gt"
    group_tag_name = "im_id"

    ds_name_to_data_pathes = {
        "PLDU-train": "/mnt/d/datasetninja-raw/pld-uav/PLDU Dataset-20230928T061029Z-001/PLDU Dataset/train/aug_data",
        "PLDU-test": "/mnt/d/datasetninja-raw/pld-uav/PLDU Dataset-20230928T061029Z-001/PLDU Dataset/test",
        "PLDM-train": "/mnt/d/datasetninja-raw/pld-uav/PLDM Dataset-20230928T061059Z-001/PLDM Dataset/train/aug_data",
        "PLDM-test": "/mnt/d/datasetninja-raw/pld-uav/PLDM Dataset-20230928T061059Z-001/PLDM Dataset/test",
    }

    def create_ann_train(image_path):
        labels = []

        im_id_value = get_file_name(image_path)
        group_id = sly.Tag(tag_id, value=im_id_value)

        aug_value = image_path.split("/")[-2]
        aug = sly.Tag(tag_aug, value=aug_value)

        ann_path = image_path.replace(images_folder, masks_folder)
        mask_path = ann_path.replace(images_ext, ann_ext)

        ann_np = sly.imaging.image.read(mask_path)[:, :, 0]
        img_height = ann_np.shape[0]
        img_wight = ann_np.shape[1]
        obj_mask = ann_np == 255
        ret, curr_mask = connectedComponents(obj_mask.astype("uint8"), connectivity=8)
        for i in range(1, ret):
            obj_mask = curr_mask == i
            curr_bitmap = sly.Bitmap(obj_mask)
            if curr_bitmap.area > 10:
                curr_label = sly.Label(curr_bitmap, obj_class)
                labels.append(curr_label)

        return sly.Annotation(
            img_size=(img_height, img_wight), labels=labels, img_tags=[aug, group_id]
        )

    def create_ann_test(image_path):
        labels = []

        image_np = sly.imaging.image.read(image_path)[:, :, 0]
        img_height = image_np.shape[0]
        img_wight = image_np.shape[1]

        mask_name = get_file_name(image_path) + masks_ext
        mask_path = os.path.join(masks_path, mask_name)

        if file_exists(mask_path):
            import scipy.io

            mat = scipy.io.loadmat(mask_path)
            mask = mat["groundTruth"][0][0][0][0][0]

            obj_mask = mask == 1
            ret, curr_mask = connectedComponents(obj_mask.astype("uint8"), connectivity=8)
            for i in range(1, ret):
                obj_mask = curr_mask == i
                curr_bitmap = sly.Bitmap(obj_mask)
                curr_label = sly.Label(curr_bitmap, obj_class)
                labels.append(curr_label)

            return sly.Annotation(img_size=(img_height, img_wight), labels=labels)

    obj_class = sly.ObjClass("power_line", sly.Bitmap)
    tag_aug = sly.TagMeta("aug", sly.TagValueType.ANY_STRING)

    project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)
    meta = sly.ProjectMeta(obj_classes=[obj_class], tag_metas=[tag_aug])

    tag_id = sly.TagMeta("im_id", sly.TagValueType.ANY_STRING)
    group_tag_meta = sly.TagMeta(group_tag_name, sly.TagValueType.ANY_STRING)
    meta = meta.add_tag_meta(group_tag_meta)
    api.project.update_meta(project.id, meta.to_json())
    api.project.images_grouping(id=project.id, enable=True, tag_name=group_tag_name)

    api.project.update_meta(project.id, meta.to_json())

    for ds_name, data_path in ds_name_to_data_pathes.items():
        dataset = api.dataset.create(project.id, ds_name, change_name_if_conflict=True)

        if ds_name in ["PLDU-train", "PLDM-train"]:
            images_pathes = glob.glob(data_path + "/*/*.jpg")

            progress = sly.Progress("Create dataset {}".format(ds_name), len(images_pathes))

            for img_pathes_batch in sly.batched(images_pathes, batch_size=batch_size):
                img_names_batch = [
                    im_path.split("/")[-2] + "_" + get_file_name_with_ext(im_path)
                    for im_path in img_pathes_batch
                ]

                img_infos = api.image.upload_paths(dataset.id, img_names_batch, img_pathes_batch)
                img_ids = [im_info.id for im_info in img_infos]

                anns = [create_ann_train(image_path) for image_path in img_pathes_batch]
                api.annotation.upload_anns(img_ids, anns)

                progress.iters_done_report(len(img_names_batch))

        else:
            images_names = os.listdir(data_path)
            masks_path = data_path + "_gt"

            progress = sly.Progress("Create dataset {}".format(ds_name), len(images_names))

            for img_names_batch in sly.batched(images_names, batch_size=batch_size):
                img_pathes_batch = [os.path.join(data_path, im_name) for im_name in img_names_batch]

                img_infos = api.image.upload_paths(dataset.id, img_names_batch, img_pathes_batch)
                img_ids = [im_info.id for im_info in img_infos]

                anns = [create_ann_test(image_path) for image_path in img_pathes_batch]
                api.annotation.upload_anns(img_ids, anns)

                progress.iters_done_report(len(img_names_batch))
    return project
