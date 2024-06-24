"""
This module provides functions to interact with and analyze weather station data
within specified geographic bounds. It includes functionality to retrieve stations,
find the station with the longest record, determine a consensus period for data,
and identify the most representative station based on specific data variables.

Functions:
    get_stations_from_bounds(bounds, n_stations=5, verbose=True, export_bbox=False)
    get_longest_station_record(bounds, n_stations=25, verbose=False)
    find_consensus_period(bounds, n_stations, verbose=False)
    find_most_representative_station(bounds, n_stations, data_to_compare, verbose=False)
"""

__all__ = ['get_stations_from_bounds', 'get_longest_station_record', 'find_consensus_period', 'find_most_representative_station']

import numpy as np
import pandas as pd
import meteostat

from shapely.geometry import Point, Polygon, LineString
from pyproj import Geod
from datetime import datetime, timedelta

def get_stations_from_bounds(bounds, n_stations=5, verbose=True, export_bbox_center=False):
    """
    Retrieves weather stations within a specified bounding box.

    Parameters:
    bounds (list or Polygon or LineString): The bounding box defined as a list of tuples,
                                            list of shapely Point objects, a shapely LineString,
                                            or a shapely Polygon.
    n_stations (int): The number of stations to return. Defaults to 5.
    verbose (bool): If True, prints detailed information about the bounding box and station count. Defaults to True.
    export_bbox (bool): If True, returns the bounding box center along with the stations. Defaults to False.

    Returns:
    pd.DataFrame: A DataFrame containing the requested number of stations.
    Point (optional): The center point of the bounding box if export_bbox is True.

    Raises:
    ValueError: If the bounds parameter is not of the expected type.
    """
    if not isinstance(n_stations, int):
        raise TypeError("n_stations must be an integer")
    if not isinstance(verbose, bool):
        raise TypeError("verbose must be a boolean")
    if not isinstance(export_bbox_center, bool):
        raise TypeError("export_bbox must be a boolean")

    lower_left, upper_right = None, None

    if isinstance(bounds, list):
        if all(isinstance(item, tuple) for item in bounds):
            lower_left, upper_right = Point(bounds[0]), Point(bounds[1])
        elif all(isinstance(item, Point) for item in bounds):
            lower_left, upper_right = bounds[0], bounds[1]
    elif isinstance(bounds, Polygon):
        minx, miny, maxx, maxy = bounds.bounds
        lower_left = Point(maxx, miny)
        upper_right = Point(minx, maxy)
    elif isinstance(bounds, LineString):
        lower_left, upper_right = bounds.coords
        lower_left = Point(lower_left)
        upper_right = Point(upper_right)
    else:
        raise ValueError("Bounds must be a list of tuples, a list of shapely Point objects, a shapely LineString or a shapely Polygon.")

    bbox_center = LineString([lower_left, upper_right]).interpolate(.5, normalized=True)
    _, _, distance = Geod(ellps='WGS84').inv(lower_left.x, lower_left.y, upper_right.x, upper_right.y)

    if verbose:
        print(f"Length of bounding box diagonal: {distance / 1000:8.2f} km")

    stats = meteostat.Stations().nearby(lat=bbox_center.x, lon=bbox_center.y, radius=distance * 0.85)
    stats = stats.inventory('daily', datetime.today() - timedelta(days=5))

    if verbose:
        print(f"Number of stations: {stats.count()}, returning top {n_stations}.")

    if export_bbox_center:
        return stats.fetch(n_stations), bbox_center
    else:
        return stats.fetch(n_stations)


def get_longest_station_record(bounds, n_stations=25, verbose=False):
    """
    Finds the weather station with the longest record within the specified bounding box.

    Parameters:
    bounds (list or Polygon or LineString): The bounding box defined as a list of tuples,
                                            list of shapely Point objects, a shapely LineString,
                                            or a shapely Polygon.
    n_stations (int): The number of stations to consider. Defaults to 25.
    verbose (bool): If True, prints detailed information. Defaults to False.

    Returns:
    pd.Series: The station with the longest record.
    """
    if not isinstance(n_stations, int):
        raise TypeError("n_stations must be an integer")
    if not isinstance(verbose, bool):
        raise TypeError("verbose must be a boolean")

    df = get_stations_from_bounds(bounds, verbose=verbose, n_stations=n_stations)
    longest_idx = np.argmin(df.daily_start)
    return df.iloc[longest_idx]


def find_consensus_period(bounds, n_stations, verbose=False):
    """
    Finds the consensus period for the weather stations within the specified bounding box.

    Parameters:
    bounds (list or Polygon or LineString): The bounding box defined as a list of tuples,
                                            list of shapely Point objects, a shapely LineString,
                                            or a shapely Polygon.
    n_stations (int): The number of stations to consider.
    verbose (bool): If True, prints detailed information. Defaults to False.

    Returns:
    tuple: A tuple containing the start and end datetime objects for the consensus period.
    """
    if not isinstance(n_stations, int):
        raise TypeError("n_stations must be an integer")
    if not isinstance(verbose, bool):
        raise TypeError("verbose must be a boolean")

    df = get_stations_from_bounds(bounds, verbose=verbose, n_stations=n_stations)
    max_start_date_daily = np.max(df.daily_start).date()
    start_datetime = datetime.combine(max_start_date_daily, datetime.min.time())

    min_end_date_daily = np.min(df.daily_end).date()
    end_datetime = datetime.combine(min_end_date_daily, datetime.max.time())

    if verbose:
        print(f"Consensus starting date: {start_datetime.date()}, consensus ending date: {end_datetime.date()}")

    return start_datetime, end_datetime


def find_most_representative_station(bounds, n_stations, data_to_compare, verbose=False):
    """
    Finds the most representative weather station based on the specified data variable.

    Parameters:
    bounds (list or Polygon or LineString): The bounding box defined as a list of tuples,
                                            list of shapely Point objects, a shapely LineString,
                                            or a shapely Polygon.
    n_stations (int): The number of stations to consider.
    data_to_compare (str): The data variable to compare (e.g., "tavg", "tmin", "tmax", "prcp").
    verbose (bool): If True, prints detailed information. Defaults to False.

    Returns:
    pd.Series: The most representative station based on the specified data variable.

    Raises:
    ValueError: If the data_to_compare parameter is not a valid variable available from meteostat.Daily.
    """
    if not isinstance(n_stations, int):
        raise TypeError("n_stations must be an integer")
    if not isinstance(data_to_compare, str):
        raise TypeError("data_to_compare must be a string")
    if not isinstance(verbose, bool):
        raise TypeError("verbose must be a boolean")

    valid_data = ["tavg", "tmin", "tmax", "prcp", "snow", "wdir", "wspd", "wpgt", "pres", "tsun"]
    if data_to_compare not in valid_data:
        raise ValueError("data_to_compare needs to be a variable available from meteostat.Daily!")

    df = get_stations_from_bounds(bounds, n_stations=n_stations, verbose=False)
    start, end = find_consensus_period(bounds, n_stations=n_stations, verbose=verbose)

    stations = [meteostat.Daily(station, start=start, end=end).fetch() for station in list(df.index)]

    base = pd.concat([d for d in stations], axis=1, join='inner').reset_index()
    base = base.loc[:, [data_to_compare in x for x in base.columns]]
    base["rowmeans"] = base.apply(np.mean, axis=1)

    squared_deviations = [((base.iloc[:, i] - base["rowmeans"])**2).sum() for i in range(n_stations)]
    most_representative_station_idx = np.argmin(squared_deviations)
    best_station = df.iloc[most_representative_station_idx]

    if verbose:
        print(f"Most representative station, based on {data_to_compare}: {best_station.loc['name']} (ID: {best_station.name})")

    return best_station
