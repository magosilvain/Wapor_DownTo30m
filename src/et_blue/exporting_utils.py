from typing import List, Tuple
import ee
from utils.ee_utils import back_to_int, export_image_to_asset
from src.et_blue.compute_et_blue import compute_et_blue
from src.et_green.exporting_utils import get_time_step_pattern, generate_export_task


def process_et_blue(
    et_collection_list: ee.List,
    et_green_list: ee.List,
    year: int,
    aoi: ee.Geometry,
    asset_path: str,
    time_step_type: str = "monthly",
    resolution: int = 10,
) -> None:
    """
    Process and export ET blue images for a given year.

    Args:
        et_collection_list (ee.List): List of ET images
        et_green_list (ee.List): List of ET green images
        year (int): Year to process
        aoi (ee.Geometry): Area of interest
        asset_path (str): Base path for asset export
        time_step_type (str): Type of time step ("monthly" or "dekadal")
        resolution (int): Export resolution in meters
    """
    tasks = []
    collection_size = ee.List(et_collection_list).size().getInfo()

    for i in range(collection_size):
        # Process ET images
        et_image = ee.Image(et_collection_list.get(i))
        et_green = ee.Image(et_green_list.get(i))

        # Get time step pattern from image date
        date = ee.Date(et_image.get("system:time_start"))
        time_step_pattern = get_time_step_pattern(date, time_step_type)

        et_blue = compute_et_blue(et_image, et_green)
        et_blue = back_to_int(et_blue, 100)

        # Create export task
        task_name = f"ET_blue_raw_{time_step_type}_{year}_{time_step_pattern}"
        task = generate_export_task(
            et_blue, asset_path, task_name, year, aoi, resolution
        )
        tasks.append(task)

    print(f"Generated {len(tasks)} export tasks for year {year}")